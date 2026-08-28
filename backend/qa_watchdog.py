import os
import sys
import asyncio
import json
import random
import time
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"): sys.stderr.reconfigure(encoding="utf-8")

DIR = r"C:\Users\gonza\.gemini\antigravity\scratch\comparador-cloudrun"
sys.path.insert(0, DIR)

from backend.scrapers_coordinator import scrapear_todas_las_farmacias
from backend.isp_engine import isp_engine
from backend.cache import get_cached_results, save_cached_results, _get_connection

CHILE_TZ = timezone(timedelta(hours=-4))

CATALOGO_SEMILLA = [
    "paracetamol 500", "ibuprofeno 400", "losartan 50", "omeprazol 20", "eutirox 100",
    "mometasona nasal 50", "rupatadina", "abrilar", "amoxicilina 500", "atorvastatina 20",
    "metformina 850", "sertralina 50", "clonazepam", "salbutamol inhalador", "ketorolaco",
    "cetirizina 10", "desloratadina 5", "loratadina 10", "enalapril 10", "aspirina 100",
    "fluticasona nasal", "diclofenaco 50", "prednisona 20", "ciprofloxacino 500", "viadil"
]

def get_incremental_catalog_sample(n: int = 10) -> list:
    """Extrae N medicamentos al azar desde nuestro Catálogo Interno Incremental."""
    catalogo_vivo = set(CATALOGO_SEMILLA)

    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT query FROM search_cache WHERE total > 0;")
        for row in cursor.fetchall():
            q = row[0].strip().lower()
            if len(q) >= 3:
                catalogo_vivo.add(q)
        conn.close()
    except Exception:
        pass

    try:
        from backend.analytics import get_db_connection
        conn_a = get_db_connection()
        cur_a = conn_a.cursor()
        cur_a.execute("SELECT DISTINCT query FROM analytics_searches;")
        for row in cur_a.fetchall():
            q_full = row[0].strip().lower()
            for part in q_full.split(","):
                part_clean = part.strip()
                if len(part_clean) >= 3:
                    catalogo_vivo.add(part_clean)
        conn_a.close()
    except Exception:
        pass

    pool_list = list(catalogo_vivo)
    return random.sample(pool_list, min(n, len(pool_list)))

def _extract_results_list(data) -> list:
    """Extrae con seguridad la lista de items desde cualquier estructura devuelta."""
    if not data:
        return []
    if isinstance(data, list):
        items = []
        for x in data:
            if isinstance(x, dict): items.append(x)
            elif isinstance(x, str):
                try: items.append(json.loads(x))
                except Exception: pass
        return items
    if isinstance(data, dict):
        return _extract_results_list(data.get("resultados", []))
    return []

async def run_random_qa_audit(sample_size: int = 10):
    muestra_aleatoria = get_incremental_catalog_sample(sample_size)
    
    print("="*85)
    print(f"🎲 AUDITORÍA DE QA DIARIA AL AZAR — CATÁLOGO INTERNO INCREMENTAL")
    print(f"⏰ Fecha/Hora: {datetime.now(CHILE_TZ).strftime('%Y-%m-%d %H:%M:%S')} (Chile)")
    print(f"📋 Muestra Seleccionada desde Búsquedas Reales de Usuarios ({len(muestra_aleatoria)} meds):")
    for idx, m in enumerate(muestra_aleatoria, 1):
        print(f"   {idx}. {m}")
    print("="*85)

    total_evaluaciones = 0
    evaluaciones_exitosas = 0
    evaluaciones_fallidas = 0
    reparaciones_cache = 0
    reporte_general = []

    for i, med in enumerate(muestra_aleatoria, 1):
        print(f"\n[{i}/{sample_size}] 🔬 Evaluando medicamento del catálogo real: '{med}'...")
        t0 = time.time()
        
        raw_cached = get_cached_results(med)
        cached_items = _extract_results_list(raw_cached)
        cached_count = len(cached_items)
        
        raw_live = await scrapear_todas_las_farmacias(med)
        elapsed = round(time.time() - t0, 2)
        live_results = _extract_results_list(raw_live)
        
        by_pharmacy = {}
        for r in live_results:
            f = r.get("fuente", "Desconocida")
            if f == "Ecofarmacia": f = "Ecofarmacias"
            by_pharmacy.setdefault(f, []).append(r)

        validados_med = []
        farmacias_detalle = {}

        for f_name in ["Cruz Verde", "Salcobrand", "Farmacias Ahumada", "Dr. Simi", "Ecofarmacias"]:
            items_f = by_pharmacy.get(f_name, [])
            validos_f = [it for it in items_f if isp_engine.match_product_against_query(it.get("nombre", ""), med)[0]]
            
            total_evaluaciones += 1
            if validos_f:
                evaluaciones_exitosas += 1
                def get_num(p):
                    return int("".join(c for c in str(p) if c.isdigit()) or 999999)
                validos_f.sort(key=lambda x: get_num(x.get("precio", "0")))
                mejor = validos_f[0]
                farmacias_detalle[f_name] = {"status": "OK", "mejor_precio": mejor.get("precio"), "producto": mejor.get("nombre")}
                validados_med.extend(validos_f)
                print(f"   🏥 {f_name:18} ──► ✅ {mejor.get('precio'):>8} ({mejor.get('nombre')[:35]}...)")
            else:
                evaluaciones_fallidas += 1
                farmacias_detalle[f_name] = {"status": "SIN_STOCK_O_FALLA"}
                print(f"   🏥 {f_name:18} ──► ⚠️ Sin stock / Sin match válido")

        if validados_med:
            cached_validos = [c for c in cached_items if isp_engine.match_product_against_query(c.get("nombre", ""), med)[0]]
            if len(cached_validos) < cached_count or cached_count == 0 or len(validados_med) > cached_count:
                save_cached_results(med, validados_med, len(validados_med))
                reparaciones_cache += 1
                print(f"   🔧 [AUTO-REPAIR] Caché interna actualizada y reparada con {len(validados_med)} productos.")

        reporte_general.append({
            "medicamento": med,
            "elapsed_seconds": elapsed,
            "farmacias": farmacias_detalle
        })

        await asyncio.sleep(1)

    tasa_exito = round((evaluaciones_exitosas / total_evaluaciones * 100), 1) if total_evaluaciones > 0 else 0.0
    estado = "🟢 EXCELENTE (HEALTHY)" if tasa_exito >= 80 else ("🟡 ADVERTENCIA (WARNING)" if tasa_exito >= 65 else "🔴 CRÍTICO")

    print("\n" + "="*85)
    print("📊 RESUMEN DE AUDITORÍA QA DE CATÁLOGO VIVO:")
    print(f"   • Total Farmacias Evaluadas: {total_evaluaciones} (10 meds x 5 farmacias)")
    print(f"   • Farmacias con Match y Stock Válido: {evaluaciones_exitosas}")
    print(f"   • Farmacias sin Stock o Error: {evaluaciones_fallidas}")
    print(f"   • Tasa de Salud Real del Sistema: {tasa_exito}%")
    print(f"   • Cachés Auto-Reparadas: {reparaciones_cache}")
    print(f"   • Diagnóstico Final: {estado}")
    print("="*85)

    return {
        "timestamp": datetime.now(CHILE_TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "tasa_exito_porcentaje": f"{tasa_exito}%",
        "estado": estado,
        "evaluaciones_exitosas": evaluaciones_exitosas,
        "evaluaciones_fallidas": evaluaciones_fallidas,
        "total_evaluaciones": total_evaluaciones,
        "reparaciones_cache": reparaciones_cache,
        "medicamentos": muestra_aleatoria
    }

if __name__ == "__main__":
    asyncio.run(run_random_qa_audit(10))
