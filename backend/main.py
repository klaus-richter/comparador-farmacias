import time
import asyncio
from typing import Optional
from fastapi import FastAPI, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.scrapers_coordinator import scrapear_todas_las_farmacias, scrapear_farmacias_especificas
from backend.cache import (
    get_cached_results,
    save_cached_results,
    get_cache_stats,
    clear_expired,
)
from backend.worker import precargar_medicamentos

MAJOR_CHAINS = ["Cruz Verde", "Salcobrand", "Farmacias Ahumada"]

app = FastAPI(title="Comparador de Precios de Farmacias API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
def hello():
    return {"status": "ok", "message": "Backend activo con 5 farmacias, auto-healing en vivo y caché SQLite diario"}

async def buscar_un_producto(prod: str, force_refresh: bool = False):
    """
    Busca un medicamento. Si está en caché vigente en el día y no se fuerza refresco, responde de inmediato.
    Auto-Healing: Si alguna de las grandes cadenas farmacéuticas (Cruz Verde, Salcobrand, Ahumada)
    carece de resultados y no tiene diagnóstico 'SIN_STOCK' confirmado, dispara un scraping en vivo
    selectivo para esa farmacia, consolida la información y repara el caché en tiempo real.
    """
    if not force_refresh:
        cached = get_cached_results(prod)
        if cached:
            resultados = cached.get("resultados", [])
            cobertura_detalle = cached.get("cobertura", {}).get("detalle", {})
            cadenas_presentes = {item.get("fuente") for item in resultados if item.get("fuente")}

            farmacias_a_sanar = []
            for cadena in MAJOR_CHAINS:
                tiene_items = any(cadena.lower() in f.lower() or f.lower() in cadena.lower() for f in cadenas_presentes)
                if not tiene_items:
                    diag = cobertura_detalle.get(cadena, {})
                    status = diag.get("status", "")
                    # Si no tiene items o tuvo error previo, re-intentar en vivo esa farmacia para no dejar falsos sin stock
                    farmacias_a_sanar.append(cadena)

            if farmacias_a_sanar:
                print(f"[Auto-Healing Seguro] Re-escaneando '{prod}' en: {farmacias_a_sanar} para descartar falso sin stock")
                nuevos_items, nuevo_detalle = await scrapear_farmacias_especificas(prod, farmacias_a_sanar, max_retries=2)
                cobertura_detalle.update(nuevo_detalle)

                # Mantener resultados de farmacias que no se re-escanearon y agregar los nuevos
                resultados_filtrados = [
                    item for item in resultados
                    if not any(f.lower() in item.get("fuente", "").lower() for f in farmacias_a_sanar)
                ]
                resultados_filtrados.extend(nuevos_items)

                con_stock = sum(1 for d in cobertura_detalle.values() if d.get("status") == "OK")
                sin_stock = sum(1 for d in cobertura_detalle.values() if d.get("status") == "SIN_STOCK")
                con_error = sum(1 for d in cobertura_detalle.values() if "ERROR" in d.get("status", ""))

                datos_actualizados = {
                    "producto": prod,
                    "total": len(resultados_filtrados),
                    "resultados": resultados_filtrados,
                    "cobertura": {
                        "total_farmacias": 5,
                        "con_stock": con_stock,
                        "sin_stock": sin_stock,
                        "con_error": con_error,
                        "detalle": cobertura_detalle
                    }
                }
                save_cached_results(prod, datos_actualizados)
                datos_actualizados["cached"] = True
                datos_actualizados["auto_healed"] = True
                return datos_actualizados

            return cached

    data = await scrapear_todas_las_farmacias(prod, max_retries=2)
    save_cached_results(prod, data)
    data["cached"] = False
    return data

@app.get("/api/buscar")
async def buscar(
    q: str = Query(..., description="Nombre del producto"),
    refresh: bool = False
):
    start = time.time()
    data = await buscar_un_producto(q, force_refresh=bool(refresh))
    elapsed = round(time.time() - start, 2)
    return {
        "status": "ok",
        "producto": q,
        "total_encontrados": data.get("total", len(data.get("resultados", []))),
        "resultados": data.get("resultados", []),
        "cobertura": data.get("cobertura", {}),
        "cached": data.get("cached", False),
        "fecha_ingesta": data.get("fecha_ingesta"),
        "elapsed_seconds": elapsed
    }

@app.get("/api/buscar-receta")
async def buscar_receta(
    q: str = Query(..., description="Medicamentos separados por coma"),
    refresh: bool = False
):
    start = time.time()
    productos = [p.strip() for p in q.replace("\n", ",").split(",") if p.strip()][:5]

    res_final = []
    todos_cacheados = True
    for p in productos:
        d = await buscar_un_producto(p, force_refresh=bool(refresh))
        if isinstance(d, dict):
            res_final.append(d)
            if not d.get("cached", False):
                todos_cacheados = False

    elapsed = round(time.time() - start, 2)
    return {
        "status": "ok",
        "total_medicamentos": len(res_final),
        "receta": res_final,
        "cached": todos_cacheados and len(res_final) > 0,
        "elapsed_seconds": elapsed
    }

@app.get("/api/cache/status")
def cache_status():
    """Retorna estado y estadísticas de la caché SQLite."""
    return {
        "status": "ok",
        "stats": get_cache_stats()
    }

@app.post("/api/cache/clean")
def cache_clean():
    """Limpia registros expirados de la caché."""
    deleted = clear_expired()
    return {"status": "ok", "deleted_expired_count": deleted}

@app.post("/api/cache/warmup")
async def cache_warmup(background_tasks: BackgroundTasks):
    """Inicia la precarga de medicamentos en segundo plano."""
    background_tasks.add_task(precargar_medicamentos)
    return {"status": "ok", "message": "Precarga de catálogo iniciada en segundo plano"}
