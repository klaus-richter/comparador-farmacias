import time
import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.scrapers.salcobrand import buscar_salcobrand
from backend.scrapers.ahumada import buscar_ahumada
from backend.scrapers.cruzverde import buscar_cruzverde
from backend.scrapers.drsimi import buscar_drsimi
from backend.scrapers.ecofarmacias import buscar_ecofarmacias

app = FastAPI(title="Comparador de Precios de Farmacias API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Semáforo global: máximo 4 browsers Playwright simultáneos (estable, confiable y seguro)
_sem = asyncio.Semaphore(4)

async def _con_sem(coro):
    async with _sem:
        return await coro

@app.get("/api/hello")
def hello():
    return {"status": "ok", "message": "Backend activo con 5 farmacias"}

async def buscar_un_producto(prod: str):
    res_salco, res_ahumada, res_cv, res_simi, res_eco = await asyncio.gather(
        _con_sem(buscar_salcobrand(prod)),
        _con_sem(buscar_ahumada(prod)),
        _con_sem(buscar_cruzverde(prod)),
        _con_sem(buscar_drsimi(prod)),
        buscar_ecofarmacias(prod),
        return_exceptions=True
    )

    resultados = []
    for res in [res_salco, res_ahumada, res_cv, res_simi, res_eco]:
        if isinstance(res, list):
            resultados.extend(res)

    return {
        "producto": prod,
        "total": len(resultados),
        "resultados": resultados
    }

@app.get("/api/buscar")
async def buscar(q: str = Query(..., description="Nombre del producto")):
    start = time.time()
    data = await buscar_un_producto(q)
    elapsed = round(time.time() - start, 2)
    return {
        "status": "ok",
        "producto": q,
        "total_encontrados": data["total"],
        "resultados": data["resultados"],
        "elapsed_seconds": elapsed
    }

@app.get("/api/buscar-receta")
async def buscar_receta(q: str = Query(..., description="Medicamentos separados por coma")):
    start = time.time()
    productos = [p.strip() for p in q.replace("\n", ",").split(",") if p.strip()]

    tasks = [buscar_un_producto(p) for p in productos]
    desglose = await asyncio.gather(*tasks, return_exceptions=True)

    res_final = []
    for d in desglose:
        if isinstance(d, dict):
            res_final.append(d)

    elapsed = round(time.time() - start, 2)
    return {
        "status": "ok",
        "total_medicamentos": len(res_final),
        "receta": res_final,
        "elapsed_seconds": elapsed
    }
