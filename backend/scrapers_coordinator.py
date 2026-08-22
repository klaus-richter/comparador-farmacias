import asyncio
import time
from typing import List, Dict, Any, Tuple
from backend.scrapers.salcobrand import buscar_salcobrand
from backend.scrapers.ahumada import buscar_ahumada
from backend.scrapers.cruzverde import buscar_cruzverde
from backend.scrapers.drsimi import buscar_drsimi
from backend.scrapers.ecofarmacias import buscar_ecofarmacias

# Semáforo para controlar concurrencia de Playwright
_BROWSER_SEMAPHORE = asyncio.Semaphore(3)

PHARMACY_SCRAPERS = [
    ("Cruz Verde", buscar_cruzverde, True),        # Nombre, función, requiere browser
    ("Salcobrand", buscar_salcobrand, True),
    ("Farmacias Ahumada", buscar_ahumada, True),
    ("Dr. Simi", buscar_drsimi, True),
    ("Ecofarmacias", buscar_ecofarmacias, False), # HTTP rápido / BeautifulSoup
]

async def _ejecutar_con_reintento(nombre: str, scraper_fn, query: str, max_retries: int = 2) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Ejecuta un scraper individual con reintento automático si falla por timeout o error de red.
    Distingue entre 0 resultados legítimos (SIN_STOCK) y fallos técnicos.
    """
    intentos = 0
    ultimo_error = None

    while intentos <= max_retries:
        intentos += 1
        try:
            res = await scraper_fn(query)
            if isinstance(res, list) and len(res) > 0:
                return res, {
                    "status": "OK",
                    "total": len(res),
                    "intentos": intentos
                }
            elif isinstance(res, list) and len(res) == 0:
                # Si retorna lista vacía en el primer intento, reintentar una vez por si fue hidratación lenta
                if intentos <= max_retries:
                    await asyncio.sleep(1.0)
                    continue
                return [], {
                    "status": "SIN_STOCK",
                    "total": 0,
                    "intentos": intentos
                }
        except Exception as e:
            ultimo_error = str(e)
            if intentos <= max_retries:
                await asyncio.sleep(1.5 * intentos)

    return [], {
        "status": "ERROR_TECNICO",
        "error": ultimo_error or "Timeout o fallo de renderizado",
        "intentos": intentos,
        "total": 0
    }

async def scrapear_todas_las_farmacias(producto: str, max_retries: int = 2) -> Dict[str, Any]:
    """
    Coordina los 5 scrapers con escalonamiento de navegadores, reintentos automáticos
    y diagnóstico completo de cobertura por farmacia.
    """
    t0 = time.time()
    
    async def _tarea_farmacia(nombre: str, scraper_fn, req_browser: bool, delay_launch: float):
        if delay_launch > 0:
            await asyncio.sleep(delay_launch)
        
        if req_browser:
            async with _BROWSER_SEMAPHORE:
                return await _ejecutar_con_reintento(nombre, scraper_fn, producto, max_retries)
        else:
            return await _ejecutar_con_reintento(nombre, scraper_fn, producto, max_retries)

    # Escalonamos ligeramente el lanzamiento de navegadores (300ms) para evitar spikes de CPU
    tasks = []
    for idx, (nombre, scraper_fn, req_browser) in enumerate(PHARMACY_SCRAPERS):
        stagger = idx * 0.3 if req_browser else 0.0
        tasks.append(_tarea_farmacia(nombre, scraper_fn, req_browser, stagger))

    respuestas = await asyncio.gather(*tasks, return_exceptions=True)

    todos_los_resultados = []
    reporte_cobertura = {}

    for (nombre, _, _), resp in zip(PHARMACY_SCRAPERS, respuestas):
        if isinstance(resp, tuple):
            items, diagnostico = resp
            reporte_cobertura[nombre] = diagnostico
            todos_los_resultados.extend(items)
        else:
            reporte_cobertura[nombre] = {
                "status": "ERROR_CRITICO",
                "error": str(resp),
                "total": 0
            }

    farmacias_con_stock = sum(1 for d in reporte_cobertura.values() if d["status"] == "OK")
    farmacias_sin_stock = sum(1 for d in reporte_cobertura.values() if d["status"] == "SIN_STOCK")
    farmacias_error = sum(1 for d in reporte_cobertura.values() if "ERROR" in d["status"])

    elapsed = round(time.time() - t0, 2)

    return {
        "producto": producto,
        "total": len(todos_los_resultados),
        "resultados": todos_los_resultados,
        "cobertura": {
            "total_farmacias": len(PHARMACY_SCRAPERS),
            "con_stock": farmacias_con_stock,
            "sin_stock": farmacias_sin_stock,
            "con_error": farmacias_error,
            "detalle": reporte_cobertura
        },
        "elapsed_seconds": elapsed
    }

async def scrapear_farmacias_especificas(producto: str, nombres_farmacias: List[str], max_retries: int = 2) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Ejecuta el scraping en vivo únicamente para una lista específica de farmacias (Auto-Healing selectivo).
    """
    farmacias_a_correr = [
        (nombre, scraper_fn, req_browser)
        for (nombre, scraper_fn, req_browser) in PHARMACY_SCRAPERS
        if any(n.lower() in nombre.lower() or nombre.lower() in n.lower() for n in nombres_farmacias)
    ]
    if not farmacias_a_correr:
        return [], {}

    async def _tarea_farmacia(nombre: str, scraper_fn, req_browser: bool, delay_launch: float):
        if delay_launch > 0:
            await asyncio.sleep(delay_launch)
        if req_browser:
            async with _BROWSER_SEMAPHORE:
                return await _ejecutar_con_reintento(nombre, scraper_fn, producto, max_retries)
        else:
            return await _ejecutar_con_reintento(nombre, scraper_fn, producto, max_retries)

    tasks = [
        _tarea_farmacia(nombre, scraper_fn, req_browser, idx * 0.2 if req_browser else 0.0)
        for idx, (nombre, scraper_fn, req_browser) in enumerate(farmacias_a_correr)
    ]
    respuestas = await asyncio.gather(*tasks, return_exceptions=True)

    nuevos_resultados = []
    nuevo_reporte = {}
    for (nombre, _, _), resp in zip(farmacias_a_correr, respuestas):
        if isinstance(resp, tuple):
            items, diagnostico = resp
            nuevo_reporte[nombre] = diagnostico
            nuevos_resultados.extend(items)
        else:
            nuevo_reporte[nombre] = {
                "status": "ERROR_CRITICO",
                "error": str(resp),
                "total": 0
            }

    return nuevos_resultados, nuevo_reporte

