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
import backend.database as db

def _extract_analytics_summary(res_list):
    """Calcula precios minimos, maximos y farmacia ganadora para auditoria."""
    all_prices = []
    for r in res_list:
        if isinstance(r, dict):
            for item in r.get("resultados", []):
                p_str = item.get("precio", "")
                digits = "".join([c for c in p_str if c.isdigit()])
                if digits:
                    val = int(digits)
                    all_prices.append((val, item.get("fuente")))
    if not all_prices:
        return None, None, None
    min_val = min(p[0] for p in all_prices)
    max_val = max(p[0] for p in all_prices)
    winner = next((p[1] for p in all_prices if p[0] == min_val), None)
    return min_val, max_val, winner

def _build_client_output(res_list):
    """
    Construye el resumen auditado de lo que se le muestra al cliente:
    Por cada medicamento: ganador con estrella, precio, link, farmacia y comparativa por cadena.
    """
    output = []
    for r in res_list:
        if not isinstance(r, dict):
            continue
        prod_name = r.get("producto", "")
        results = r.get("resultados", [])
        
        by_pharmacy = {}
        winner = None
        min_price = float("inf")

        for item in results:
            fuente = item.get("fuente", "")
            p_str = item.get("precio", "")
            digits = "".join([c for c in str(p_str) if c.isdigit()])
            p_num = int(digits) if digits else float("inf")

            if fuente not in by_pharmacy or p_num < by_pharmacy[fuente].get("precio_num", float("inf")):
                by_pharmacy[fuente] = {
                    "precio_num": p_num,
                    "precio": p_str,
                    "titulo": item.get("titulo", ""),
                    "url": item.get("url", "")
                }

            if 0 < p_num < min_price:
                min_price = p_num
                winner = {
                    "farmacia": fuente,
                    "titulo": item.get("titulo", ""),
                    "precio": p_num,
                    "precio_formato": p_str,
                    "url": item.get("url", ""),
                    "tiene_estrella": True
                }

        for f in by_pharmacy:
            by_pharmacy[f].pop("precio_num", None)

        output.append({
            "medicamento": prod_name,
            "ganador_estrella": winner,
            "opciones_farmacias": by_pharmacy
        })
    return output

def _record_visit_and_check_block(ip: str, country: str, city: str, user_agent: str):
    try:
        is_blocked, unblock_ts = db.record_client_visit(ip, country, city, user_agent)
        if is_blocked and unblock_ts:
            _BLOCKED_IPS_STORE[ip] = unblock_ts
    except Exception as e:
        pass


from fastapi.staticfiles import StaticFiles
import os

MAJOR_CHAINS = ["Cruz Verde", "Salcobrand", "Farmacias Ahumada"]

app = FastAPI(title="Comparador de Precios de Farmacias API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://quefarmacia.cl",
        "https://www.quefarmacia.cl",
        "https://recetachile.cl",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

import threading
from zoneinfo import ZoneInfo
from datetime import datetime
from collections import defaultdict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

SANTIAGO_TZ = ZoneInfo("America/Santiago")

# Rate Limiting estricto por IP en memoria + persistido en Supabase
_RATE_LIMIT_STORE = defaultdict(list)
_BLOCKED_IPS_STORE = {}
_MAX_REQUESTS_PER_MINUTE = 10
_MAX_REQUESTS_PER_HOUR = 20

def _format_block_message(unblock_time: float, motivo: str = None) -> str:
    dt = datetime.fromtimestamp(unblock_time, SANTIAGO_TZ)
    hora_str = dt.strftime("%H:%M")
    if motivo:
        return f"Has superado el límite de {motivo}. Podrás volver a buscar a las {hora_str} hrs."
    return f"Has superado el límite de consultas permitidas. Podrás volver a buscar a las {hora_str} hrs."


@app.on_event("startup")
def preload_blocked_ips():
    """Carga bloqueos vigentes desde Supabase al arrancar el contenedor."""
    try:
        active = db.get_active_blocked_ips()
        if active:
            _BLOCKED_IPS_STORE.update(active)
    except Exception:
        pass

def _cors_429(content: dict, request: Request) -> JSONResponse:
    origin = request.headers.get("origin") or "*"
    allowed_origins = [
        "https://quefarmacia.cl", "https://www.quefarmacia.cl", "https://recetachile.cl",
        "http://localhost:5500", "http://127.0.0.1:5500"
    ]
    headers = {
        "Access-Control-Allow-Origin": origin if origin in allowed_origins else "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }
    return JSONResponse(status_code=429, content=content, headers=headers)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Proteger endpoints de búsqueda contra scrapers, bots y spam
    if request.url.path.startswith("/api/buscar"):
        client_ip = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
        client_ip = client_ip.split(",")[0].strip()
        now = time.time()

        # 0. Chequeo si la IP está en periodo de bloqueo de 1 hora
        if client_ip in _BLOCKED_IPS_STORE:
            unblock_time = _BLOCKED_IPS_STORE[client_ip]
            if now < unblock_time:
                # Si en memoria figura bloqueada, verificar en Supabase si fue desbloqueada manualmente
                try:
                    active_db = db.get_active_blocked_ips()
                    if client_ip not in active_db:
                        del _BLOCKED_IPS_STORE[client_ip]
                        if client_ip in _RATE_LIMIT_STORE:
                            _RATE_LIMIT_STORE[client_ip].clear()
                    else:
                        return _cors_429({
                            "status": "error",
                            "code": "IP_BLOCKED",
                            "detail": _format_block_message(unblock_time)
                        }, request)
                except Exception:
                    return _cors_429({
                        "status": "error",
                        "code": "IP_BLOCKED",
                        "detail": _format_block_message(unblock_time)
                    }, request)
            else:
                del _BLOCKED_IPS_STORE[client_ip]

        # Filtrar timestamps de la última hora
        timestamps = [t for t in _RATE_LIMIT_STORE[client_ip] if now - t < 3600]
        _RATE_LIMIT_STORE[client_ip] = timestamps

        # 1. Chequeo límite por minuto (máx 10)
        recent_1m = [t for t in timestamps if now - t < 60]
        if len(recent_1m) >= _MAX_REQUESTS_PER_MINUTE:
            unblock_time = now + 3600  # Bloquear por 1 hora
            _BLOCKED_IPS_STORE[client_ip] = unblock_time
            threading.Thread(target=db.block_ip, args=(client_ip, 1, "RATE_LIMIT_10_PER_MIN"), daemon=True).start()
            return _cors_429({
                "status": "error",
                "code": "RATE_LIMIT_MINUTE",
                "detail": _format_block_message(unblock_time, "10 consultas por minuto")
            }, request)

        # 2. Chequeo límite por hora (máx 20)
        if len(timestamps) >= _MAX_REQUESTS_PER_HOUR:
            unblock_time = now + 3600  # Bloquear por 1 hora
            _BLOCKED_IPS_STORE[client_ip] = unblock_time
            threading.Thread(target=db.block_ip, args=(client_ip, 1, "RATE_LIMIT_20_PER_HOUR"), daemon=True).start()
            return _cors_429({
                "status": "error",
                "code": "RATE_LIMIT_HOUR",
                "detail": _format_block_message(unblock_time, "20 consultas por hora")
            }, request)

        _RATE_LIMIT_STORE[client_ip].append(now)

    response = await call_next(request)
    return response



@app.get("/api/hello")
def hello():
    return {"status": "ok", "message": "Backend activo con 5 farmacias, rate limiting y caché"}

@app.get("/api/security/status")
async def security_status(request: Request):
    """Consulta rápida en memoria si la IP actual está bloqueada."""
    client_ip = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
    client_ip = client_ip.split(",")[0].strip()
    now = time.time()
    no_cache_headers = {
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache"
    }
    if client_ip in _BLOCKED_IPS_STORE:
        unblock_time = _BLOCKED_IPS_STORE[client_ip]
        if now < unblock_time:
            # Si en memoria figura bloqueada, verificar en Supabase si fue desbloqueada manualmente
            try:
                active_db = db.get_active_blocked_ips()
                if client_ip not in active_db:
                    del _BLOCKED_IPS_STORE[client_ip]
                    if client_ip in _RATE_LIMIT_STORE:
                        _RATE_LIMIT_STORE[client_ip].clear()
                else:
                    return _cors_429({
                        "blocked": True,
                        "detail": _format_block_message(unblock_time)
                    }, request)
            except Exception:
                return _cors_429({
                    "blocked": True,
                    "detail": _format_block_message(unblock_time)
                }, request)
        else:
            del _BLOCKED_IPS_STORE[client_ip]
    return JSONResponse(status_code=200, content={"blocked": False, "status": "ok"}, headers=no_cache_headers)

@app.get("/api/security/unblock")
@app.post("/api/security/unblock")
def unblock_client_ip(request: Request, ip: str = None):
    """Desbloquea una IP inmediatamente en memoria y en Supabase."""
    target_ip = (ip or request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")).split(",")[0].strip()
    if target_ip in _BLOCKED_IPS_STORE:
        del _BLOCKED_IPS_STORE[target_ip]
    if target_ip in _RATE_LIMIT_STORE:
        _RATE_LIMIT_STORE[target_ip].clear()
    _BLOCKED_IPS_STORE.clear()
    _RATE_LIMIT_STORE.clear()
    db.unblock_ip(target_ip)
    origin = request.headers.get("origin") or "*"
    headers = {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Cache-Control": "no-store, no-cache, must-revalidate"
    }
    return JSONResponse(status_code=200, content={"status": "ok", "unblocked": target_ip}, headers=headers)




ALL_TARGET_PHARMACIES = ["Cruz Verde", "Salcobrand", "Farmacias Ahumada", "Dr. Simi", "Ecofarmacias"]

async def buscar_un_producto(prod: str, force_refresh: bool = False):
    """
    Busca un medicamento con Auto-Healing:
    1. Si está en caché y TIENE cobertura de las 5 farmacias, responde en <0.05s.
    2. Si está en caché pero ALGUNA farmacia está vacía/sin stock (ej: Salcobrand no scrapeó anoche),
       ejecuta auto-healing selectivo solo para las farmacias faltantes y auto-repara la caché.
    3. Si no está en caché o force_refresh=True, ejecuta scraping completo.
    """
    if not force_refresh:
        cached = get_cached_results(prod)
        if cached and cached.get("total", 0) > 0:
            existing_results = cached.get("resultados", [])
            present_pharmacies = {item.get("fuente") for item in existing_results if item.get("fuente")}
            missing = [f for f in ALL_TARGET_PHARMACIES if f not in present_pharmacies]

            # Si todas las farmacias están presentes en el caché, responder de inmediato
            if not missing:
                return cached

            # Auto-healing selectivo: solo scrapear las farmacias que faltan
            try:
                nuevos_items, nuevo_diag = await scrapear_farmacias_especificas(prod, missing)
                
                # Update cobertura with the new diagnostics
                if "cobertura" not in cached:
                    cached["cobertura"] = {"detalle": {}}
                if "detalle" not in cached["cobertura"]:
                    cached["cobertura"]["detalle"] = {}
                
                for farmacia, diag in nuevo_diag.items():
                    cached["cobertura"]["detalle"][farmacia] = diag
                
                # Recalculate totals
                detalle = cached["cobertura"]["detalle"]
                cached["cobertura"]["con_stock"] = sum(1 for d in detalle.values() if d.get("status") == "OK")
                cached["cobertura"]["sin_stock"] = sum(1 for d in detalle.values() if d.get("status") == "SIN_STOCK")
                cached["cobertura"]["con_error"] = sum(1 for d in detalle.values() if d.get("status") == "ERROR")

                if nuevos_items:
                    existing_results.extend(nuevos_items)
                    cached["resultados"] = existing_results
                    cached["total"] = len(existing_results)

                # Siempre guardamos el caché porque la cobertura pudo haber cambiado
                save_cached_results(prod, cached)
                return cached
            except Exception as e:
                print(f"[AUTO-HEALING ERROR] {e}")
                return cached

    data = await scrapear_todas_las_farmacias(prod, max_retries=1)
    save_cached_results(prod, data)
    data["cached"] = False
    return data

@app.get("/api/buscar")
async def buscar(
    request: Request,
    background_tasks: BackgroundTasks,
    q: str = Query(..., description="Nombre del producto"),
    refresh: bool = False
):
    start = time.time()
    data = await buscar_un_producto(q, force_refresh=bool(refresh))
    elapsed = round(time.time() - start, 2)

    # Telemetria & Seguridad en Background (Supabase + Memory)
    client_ip = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
    client_ip = client_ip.split(",")[0].strip()
    country = request.headers.get("cf-ipcountry", "CL")
    city = request.headers.get("cf-ipcity", "Unknown")
    ua = request.headers.get("user-agent", "")

    background_tasks.add_task(_record_visit_and_check_block, client_ip, country, city, ua)
    min_p, max_p, winner = _extract_analytics_summary([data])
    results_list = data.get("resultados", [])
    output_res = _build_client_output([data])
    background_tasks.add_task(db.upsert_canasta_medicamento, q, results_list)
    background_tasks.add_task(
        db.log_search,
        ip=client_ip,
        raw_query=q,
        is_cached=data.get("cached", False),
        response_time_ms=int(elapsed * 1000),
        status="SUCCESS" if results_list else "NO_RESULTS",
        cheapest_pharmacy=winner,
        min_price=min_p,
        max_price=max_p,
        session_id=request.headers.get("x-session-id"),
        total_results=len(results_list),
        raw_products_json=results_list,
        output_json=output_res
    )

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
    request: Request,
    background_tasks: BackgroundTasks,
    q: str = Query(..., description="Medicamentos separados por coma"),
    refresh: bool = False
):
    start = time.time()
    productos = [p.strip() for p in q.replace("\n", ",").split(",") if p.strip()][:10]

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

    # Telemetria & Seguridad en Background (Supabase + Memory)
    client_ip = request.headers.get("cf-connecting-ip") or request.headers.get("x-forwarded-for") or (request.client.host if request.client else "unknown")
    client_ip = client_ip.split(",")[0].strip()
    country = request.headers.get("cf-ipcountry", "CL")
    city = request.headers.get("cf-ipcity", "Unknown")
    ua = request.headers.get("user-agent", "")

    background_tasks.add_task(_record_visit_and_check_block, client_ip, country, city, ua)
    min_p, max_p, winner = _extract_analytics_summary(res_final)
    total_found = sum(len(r.get("resultados", [])) for r in res_final if isinstance(r, dict))
    output_res = _build_client_output(res_final)
    background_tasks.add_task(db.save_recipe_to_canasta, res_final)
    background_tasks.add_task(
        db.log_search,
        ip=client_ip,
        raw_query=q,
        is_cached=todos_cacheados and len(res_final) > 0,
        response_time_ms=int(elapsed * 1000),
        status="SUCCESS" if total_found > 0 else "NO_RESULTS",
        cheapest_pharmacy=winner,
        min_price=min_p,
        max_price=max_p,
        session_id=request.headers.get("x-session-id"),
        total_results=total_found,
        raw_products_json=res_final,
        output_json=output_res
    )


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
@app.post("/api/nightly/update")
@app.get("/api/nightly/update")
async def trigger_daily_sync():
    """⛔ DESACTIVADO: Scraping masivo sin proxies residenciales quema la IP de Google Cloud."""
    return {
        "status": "disabled",
        "message": "⛔ Sync nocturno desactivado hasta integrar proxies residenciales. Sin proxies = ban de Cloudflare."
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




@app.post("/api/cache/reset")
def cache_reset():
    """Respalda la caché actual y crea una nueva desde 0."""
    import os
    import shutil
    import datetime
    from backend.cache import DB_PATH, init_db
    
    backup_path = f"{DB_PATH}.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, backup_path)
        os.remove(DB_PATH)
        
    init_db()
    return {"status": "ok", "message": "Caché reiniciada desde cero.", "backup_file": backup_path}

@app.get("/api/visitas")
def get_visits():
    from backend.cache import increment_and_get_visits
    count = increment_and_get_visits()
    return {"visitas": count}


@app.get("/api/isp/resolve")
def resolve_isp(q: str = Query(..., description="Nombre del medicamento o principio activo")):
    """Consulta semántica oficial al registro farmacéutico del ISP Chile."""
    from backend.isp_engine import isp_engine
    return isp_engine.resolve_term(q)

# ==============================================================================
# ENDPOINTS DE TELEMETRÍA Y ANALÍTICA
# ==============================================================================
from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi.responses import HTMLResponse, Response
from backend.analytics import (
    record_search, record_click, get_metrics_summary, 
    export_searches_csv, export_clicks_csv
)

class SearchEvent(BaseModel):
    query: str
    med_count: int = 1
    elapsed_ms: int = 0
    is_cache: bool = False
    winner_pharmacy: Optional[str] = None
    winner_price: Optional[str] = None
    coverage: Optional[Dict[str, Any]] = None
    user_agent: Optional[str] = ""

class ClickEvent(BaseModel):
    medicine: str
    pharmacy: str
    price: Optional[str] = None
    url: Optional[str] = None
    is_cheapest: bool = False

@app.post("/api/analytics/search")
async def track_search_event(event: SearchEvent, request: Request):
    ua = event.user_agent or request.headers.get("user-agent", "")
    record_search(
        query=event.query,
        med_count=event.med_count,
        elapsed_ms=event.elapsed_ms,
        is_cache=event.is_cache,
        winner_pharmacy=event.winner_pharmacy,
        winner_price=event.winner_price,
        coverage=event.coverage,
        user_agent=ua
    )
    return {"status": "ok"}

@app.post("/api/analytics/click")
async def track_click_event():
    # Desactivado temporalmente para no consumir procesos en clicks
    return {"status": "ok"}



@app.get("/api/admin/metrics")
def get_metrics_json():
    """Métricas en formato JSON para APIs o dashboards."""
    return get_metrics_summary()

@app.get("/api/admin/metrics/searches.csv")
def download_searches_csv():
    """Descarga el registro completo de búsquedas en CSV."""
    csv_data = export_searches_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=busquedas_comparador.csv"}
    )

@app.get("/api/admin/metrics/clicks.csv")
def download_clicks_csv():
    """Descarga el registro completo de clics y compras en CSV."""
    csv_data = export_clicks_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=clicks_compras.csv"}
    )

@app.get("/api/admin/metrics/dashboard", response_class=HTMLResponse)
def get_metrics_dashboard():
    """Panel visual interactivo de métricas y salud del comparador."""
    data = get_metrics_summary()
    gen = data["generales"]
    horas = data["horarios_chile"]
    top_q = data["top_busquedas"]
    clicks_f = data["clicks_por_farmacia"]
    winners = data["farmacias_mas_economicas_ganadas"]

    top_q_html = "".join([f"<tr><td><strong>{i+1}. {q['query'].title()}</strong></td><td style='text-align:right;'>{q['count']} veces</td></tr>" for i, q in enumerate(top_q)]) or "<tr><td colspan='2'>Sin búsquedas aún</td></tr>"
    clicks_html = "".join([f"<tr><td><strong>{c['pharmacy']}</strong></td><td style='text-align:right;'>{c['clicks']} clics</td></tr>" for c in clicks_f]) or "<tr><td colspan='2'>Sin clics aún</td></tr>"
    winners_html = "".join([f"<tr><td><strong>🏆 {w['pharmacy']}</strong></td><td style='text-align:right;'>{w['wins']} recetas ganadas</td></tr>" for w in winners]) or "<tr><td colspan='2'>Sin datos</td></tr>"
    
    peak_str = ", ".join(horas["horas_peak"]) if horas["horas_peak"] else "Calculando..."

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <title>📊 Panel de Métricas y Salud — Comparador Farmacias</title>
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 30px 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ font-size: 1.8rem; margin-bottom: 5px; }}
        p.sub {{ color: #64748b; margin-top: 0; margin-bottom: 25px; }}
        .cards-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .card {{ background: white; border-radius: 12px; padding: 18px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }}
        .card .title {{ font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 700; }}
        .card .val {{ font-size: 1.8rem; font-weight: 800; color: #0284c7; margin-top: 5px; }}
        .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 20px; margin-bottom: 25px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }}
        .btn {{ display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; background: #0284c7; color: white; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.85rem; }}
        .btn-group {{ margin-bottom: 20px; display: flex; gap: 10px; }}
      </style>
    </head>
    <body>
      <div class="container">
        <h1>📊 Panel de Analítica y Salud del Comparador</h1>
        <p class="sub">Telemetría en tiempo real de búsquedas, horas peak en Chile y tasa de éxito.</p>
        
        <div class="btn-group">
          <a href="/api/admin/metrics/searches.csv" class="btn">📥 Descargar Búsquedas (.CSV)</a>
          <a href="/api/admin/metrics/clicks.csv" class="btn">📥 Descargar Clics de Compra (.CSV)</a>
          <a href="/api/admin/daily-sync" class="btn" style="background:#16a34a;">🔄 Forzar Sync 3 AM</a>
          <a href="/api/admin/qa-audit" class="btn" style="background:#7c3aed;">🎲 Test QA 10 Meds Azar</a>
        </div>

        <div class="cards-grid">
          <div class="card">
            <div class="title">Búsquedas Hoy</div>
            <div class="val">{gen['busquedas_hoy']}</div>
          </div>
          <div class="card">
            <div class="title">Búsquedas del Mes</div>
            <div class="val">{gen['busquedas_mes']}</div>
          </div>
          <div class="card">
            <div class="title">Clics a Farmacias ↗</div>
            <div class="val">{gen['total_clicks_compra']}</div>
          </div>
          <div class="card">
            <div class="title">Salud de Scrapers</div>
            <div class="val" style="color:#16a34a;">{gen['salud_scrapers_porcentaje']}</div>
          </div>
        </div>

        <div class="grid-2">
          <div class="card">
            <div class="title">🔥 Top Medicamentos Más Buscados</div>
            <p style="font-size:0.8rem; color:#64748b;">(Estos términos alimentan automáticamente el cron nocturno de las 3:00 AM)</p>
            <table>{top_q_html}</table>
          </div>

          <div class="card">
            <div class="title">🛒 Preferencia de Compra (Clics ↗)</div>
            <p style="font-size:0.8rem; color:#64748b;">(Farmacias elegidas por los usuarios al ver precios)</p>
            <table>{clicks_html}</table>
          </div>
        </div>

        <div class="grid-2">
          <div class="card">
            <div class="title">🏆 Farmacias Más Económicas (#1)</div>
            <table>{winners_html}</table>
          </div>

          <div class="card">
            <div class="title">⏰ Horas Peak en Chile</div>
            <p style="font-size:1.1rem; font-weight:700; color:#0f172a; margin-top:10px;">{peak_str}</p>
            <p style="font-size:0.85rem; color:#64748b;">Horas recomendadas para mantenimiento: 02:00 a 05:00 AM</p>
          </div>
        </div>
      </div>
    </body>
    </html>
    """

@app.post("/api/admin/qa-audit")
@app.get("/api/admin/qa-audit")
async def trigger_qa_audit():
    """⛔ DESACTIVADO: QA audit sin proxies residenciales quema la IP de Google Cloud."""
    return {
        "status": "disabled",
        "message": "⛔ QA audit desactivado hasta integrar proxies residenciales."
    }

# Montar frontend estático al final para no interferir con endpoints API
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

