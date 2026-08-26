import os
import sys
import json
import time
import random
import asyncio
from datetime import datetime

# Añadir el directorio raíz al PATH
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, BACKEND_DIR)

from scrapers_coordinator import scrape_todas_las_farmacias

SEED_PATH = os.path.join(BACKEND_DIR, "data", "catalog_seed.json")

async def run_daily_update():
    if not os.path.exists(SEED_PATH):
        print(f"No se encontró el archivo de catálogo en {SEED_PATH}")
        return

    with open(SEED_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    total_meds = len(catalog)
    print(f"🌙 [3:00 AM] Iniciando actualización nocturna indetectable para {total_meds} medicamentos...")

    iso_now = datetime.now().isoformat()
    updated_catalog = []

    for idx, item in enumerate(catalog, 1):
        query = item.get("query")
        print(f"[{idx}/{total_meds}] Consultando '{query}'...")
        try:
            resultados, cobertura = await scrape_todas_las_farmacias(query)
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
                # Mantener registro previo si hubo timeout temporal
                updated_catalog.append(item)
                print("  ⚠️ Sin resultados en vivo hoy, manteniendo versión previa.")
        except Exception as e:
            print(f"  ❌ Error consultando '{query}': {e}")
            updated_catalog.append(item)

        # 1. Jitter aleatorio humano (entre 1.8s y 3.5s)
        human_delay = random.uniform(1.8, 3.5)
        await asyncio.sleep(human_delay)

        # 2. Micro-descanso cada 15 medicamentos (8 a 12s) para no levantar sospechas
        if idx % 15 == 0 and idx < total_meds:
            rest_delay = random.uniform(8.0, 12.0)
            print(f"  ☕ Micro-pausa de {rest_delay:.1f}s simulando descanso de usuario...")
            await asyncio.sleep(rest_delay)

    # Guardar catálogo actualizado
    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_catalog, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] Actualización nocturna completada: {len(updated_catalog)} medicamentos actualizados.")

if __name__ == "__main__":
    asyncio.run(run_daily_update())
