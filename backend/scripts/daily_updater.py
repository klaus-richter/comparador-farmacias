import os
import sys
import json
import time
import random
import asyncio
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, BACKEND_DIR)

from scrapers_coordinator import scrapear_todas_las_farmacias

SEED_PATH = os.path.join(BACKEND_DIR, "data", "catalog_seed.json")

# Medicamentos testigo obligatorios que siempre existen en farmacias
WITNESS_MEDS = ["paracetamol", "omeprazol", "ibuprofeno", "amoxicilina", "losartan"]
PHARMACIES = ["Cruz Verde", "Salcobrand", "Farmacias Ahumada", "Dr. Simi", "Ecofarmacias"]

async def run_daily_update():
    if not os.path.exists(SEED_PATH):
        print(f"No se encontró el archivo de catálogo en {SEED_PATH}")
        return

    with open(SEED_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    total_meds = len(catalog)
    print(f"🌙 [3:00 AM] Iniciando actualización nocturna para {total_meds} medicamentos...")

    iso_now = datetime.now().isoformat()
    updated_catalog = []

    stats = {p: {"hits": 0, "searches": 0} for p in PHARMACIES}
    witness_stats = {p: {"hits": 0, "searches": 0} for p in PHARMACIES}

    for idx, item in enumerate(catalog, 1):
        query = item.get("query", "").strip()
        print(f"\n[{idx}/{total_meds}] Consultando: '{query}'...")
        is_witness = query.lower() in WITNESS_MEDS

        try:
            data = await scrapear_todas_las_farmacias(query)
            resultados = data.get("resultados", [])
            cobertura = data.get("cobertura", {})

            for p in PHARMACIES:
                stats[p]["searches"] += 1
                if is_witness:
                    witness_stats[p]["searches"] += 1

                found_in_pharm = any(p.lower() in (it.get("fuente", "")).lower() for it in resultados)
                if found_in_pharm:
                    stats[p]["hits"] += 1
                    if is_witness:
                        witness_stats[p]["hits"] += 1

            if resultados:
                clean_results = []
                for it in resultados:
                    clean_results.append({
                        "nombre": it.get("nombre", ""),
                        "precio": it.get("precio", ""),
                        "url": it.get("url", ""),
                        "fuente": it.get("fuente", ""),
                        "disponible": it.get("disponible", True)
                    })

                payload = json.dumps({
                    "resultados": clean_results,
                    "cobertura": cobertura
                }, ensure_ascii=False)

                updated_catalog.append({
                    "query": query,
                    "data_json": payload,
                    "total": len(clean_results),
                    "fecha_ingesta": iso_now
                })
                print(f"  ✓ {len(clean_results)} productos actualizados.")
            else:
                updated_catalog.append(item)
                print("  ⚠️ Sin resultados en vivo hoy, manteniendo versión previa.")

        except Exception as e:
            print(f"  ❌ Error consultando '{query}': {e}")
            updated_catalog.append(item)

        # Jitter aleatorio humano (1.8s a 3.5s)
        await asyncio.sleep(random.uniform(1.8, 3.5))

        # Micro-pausa cada 15 medicamentos
        if idx % 15 == 0 and idx < total_meds:
            rest_delay = random.uniform(8.0, 12.0)
            print(f"  ☕ Micro-pausa de {rest_delay:.1f}s...")
            await asyncio.sleep(rest_delay)

    # Guardar catálogo actualizado
    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_catalog, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Actualización nocturna guardada en {SEED_PATH}")

    # =========================================================================
    # 🔍 EVALUACIÓN DE FALLAS GRAVES (SOLO SI ES GRAVE Y REQUIERE HOTFIX)
    # =========================================================================
    print("\n" + "="*60)
    print("📊 INFORME DE SALUD DE SCRAPERS:")
    print("="*60)

    severe_failures = []

    for p in PHARMACIES:
        total_s = stats[p]["searches"]
        hits = stats[p]["hits"]
        rate = (hits / total_s * 100) if total_s > 0 else 0
        
        w_total = witness_stats[p]["searches"]
        w_hits = witness_stats[p]["hits"]

        print(f"🏛️ {p:20} -> Éxito global: {hits}/{total_s} ({rate:.1f}%) | Testigos: {w_hits}/{w_total}")

        # CRITERIO DE FALLA GRAVE:
        # 1. Si la farmacia tuvo 0 hits en los medicamentos testigo
        # 2. O si en un catálogo >= 10 medicamentos, la tasa de éxito fue menor al 15% (excepto Dr. Simi)
        if w_total >= 3 and w_hits == 0 and p != "Dr. Simi":
            severe_failures.append(f"❌ {p}: 0/{w_total} aciertos en medicamentos testigo básicos (Posible cambio de selectores HTML o bloqueo).")
        elif total_s >= 10 and rate < 15.0 and p != "Dr. Simi":
            severe_failures.append(f"❌ {p}: Tasa de éxito crítica de {rate:.1f}% ({hits}/{total_s} medicamentos).")

    # Generar Step Summary en GitHub Actions si aplica
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as sf:
            sf.write("## 🌙 Informe de Actualización Nocturna\n\n")
            sf.write(f"- **Medicamentos procesados:** {total_meds}\n")
            sf.write(f"- **Fecha:** {datetime.now().strftime('%d-%m-%Y %H:%M')}\n\n")
            sf.write("| Farmacia | Éxito Global | Medicamentos Testigo |\n")
            sf.write("| :--- | :--- | :--- |\n")
            for p in PHARMACIES:
                sf.write(f"| {p} | {stats[p]['hits']}/{stats[p]['searches']} | {witness_stats[p]['hits']}/{witness_stats[p]['searches']} |\n")
            
            if severe_failures:
                sf.write("\n### 🚨 ALERTA CRÍTICA: Fallas Graves Detectadas\n")
                for f_msg in severe_failures:
                    sf.write(f"- {f_msg}\n")

    if severe_failures:
        print("\n" + "🚨"*30)
        print("🚨 SE DETECTARON FALLAS GRAVES QUE REQUIEREN HOTFIX:")
        for f_msg in severe_failures:
            print(f"  {f_msg}")
        print("🚨"*30)
        sys.exit(1)
    else:
        print("\n✅ Todos los scrapers operaron con normalidad. No se requiere intervención.")

if __name__ == "__main__":
    asyncio.run(run_daily_update())
