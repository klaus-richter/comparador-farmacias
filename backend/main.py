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

from fastapi.staticfiles import StaticFiles
import os

MAJOR_CHAINS = ["Cruz Verde", "Salcobrand", "Farmacias Ahumada"]

app = FastAPI(title="Comparador de Precios de Farmacias API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# Rate Limiting ultra liviano en memoria por IP (0ms latencia)
_RATE_LIMIT_STORE = defaultdict(list)
_MAX_REQUESTS_PER_MINUTE = 15

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Proteger endpoints de búsqueda contra ataques DoS o bombardeo de bots
    if request.url.path.startswith("/api/buscar"):
        client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
        client_ip = client_ip.split(",")[0].strip()
        now = time.time()

        # Limpiar marcas de tiempo de más de 60 segundos
        _RATE_LIMIT_STORE[client_ip] = [t for t in _RATE_LIMIT_STORE[client_ip] if now - t < 60]

        if len(_RATE_LIMIT_STORE[client_ip]) >= _MAX_REQUESTS_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "detail": "Has realizado demasiadas búsquedas seguidas. Por favor espera un momento."
                }
            )
        _RATE_LIMIT_STORE[client_ip].append(now)

    response = await call_next(request)
    return response

@app.get("/api/hello")
def hello():
    return {"status": "ok", "message": "Backend activo con 5 farmacias, rate limiting y caché"}



async def buscar_un_producto(prod: str, force_refresh: bool = False):
    """
    Busca un medicamento. Si está en base de datos con resultados responde de inmediato (<0.05s).
    Si no existe O si la caché tiene 0 resultados (scraping previo fallido), ejecuta scraping en vivo.
    """
    if not force_refresh:
        cached = get_cached_results(prod)
        # Solo retornar caché si tiene resultados reales. Si total==0, re-intentar.
        if cached and cached.get("total", 0) > 0:
            return cached

    data = await scrapear_todas_las_farmacias(prod, max_retries=1)
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

    # Ejecutar la búsqueda de todos los medicamentos en paralelo controlado
    tasks = [buscar_un_producto(p, force_refresh=bool(refresh)) for p in productos]
    resultados = await asyncio.gather(*tasks, return_exceptions=True)

    res_final = []
    todos_cacheados = True
    for r in resultados:
        if isinstance(r, dict):
            res_final.append(r)
            if not r.get("cached", False):
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


@app.post("/api/admin/daily-sync")
@app.get("/api/admin/daily-sync")
async def trigger_daily_sync():
    """Endpoint para activar la actualización nocturna a las 3:00 AM (desde Cloud Scheduler o Cron)."""
    try:
        from backend.scripts.daily_updater import run_daily_update
        asyncio.create_task(run_daily_update())
        return {
            "status": "ok",
            "message": "🌙 Actualización nocturna iniciada exitosamente en segundo plano con protección anti-bot."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


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

# Montar frontend para pruebas locales inmediatas en http://localhost:8000
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

