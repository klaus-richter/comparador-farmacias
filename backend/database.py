import os
import re
import json
import logging
import unicodedata
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

SANTIAGO_TZ = ZoneInfo("America/Santiago")

logger = logging.getLogger("backend.database")

# URL de conexion a Supabase PostgreSQL (Transaction Pooler - IPv4)
DEFAULT_DB_URL = "postgresql://postgres.vctauoyvjxxqwfcpdqbq:0j9mCGNoNGSf0JXH@aws-0-us-west-2.pooler.supabase.com:6543/postgres"
DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DB_URL)

_has_psycopg2 = False
try:
    import psycopg2
    from psycopg2.extras import Json
    _has_psycopg2 = True
except ImportError:
    logger.warning("psycopg2 no esta instalado. Operaciones de BD seran simuladas.")

def _get_connection():
    if not _has_psycopg2 or not DATABASE_URL:
        return None
    try:
        return psycopg2.connect(DATABASE_URL, connect_timeout=4)
    except Exception as e:
        logger.error(f"[DB CONNECT ERROR] {e}")
        return None

def parse_user_agent(ua_string: str) -> Tuple[bool, str]:
    """Detecta si es movil y el sistema operativo a partir del User-Agent."""
    if not ua_string:
        return False, "Unknown"
    ua = ua_string.lower()
    is_mobile = any(m in ua for m in ["mobile", "android", "iphone", "ipad", "ipod"])
    
    os_name = "Other"
    if "iphone" in ua or "ipad" in ua or "ios" in ua:
        os_name = "iOS"
    elif "android" in ua:
        os_name = "Android"
    elif "windows" in ua:
        os_name = "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        os_name = "macOS"
    elif "linux" in ua:
        os_name = "Linux"
        
    return is_mobile, os_name

def record_client_visit(ip: str, country: str = "CL", city: str = "Unknown", user_agent: str = "") -> Tuple[bool, Optional[float]]:
    """
    Registra o actualiza la visita del cliente en security_ips.
    Retorna (is_blocked, unblock_timestamp_unix).
    """
    conn = _get_connection()
    if not conn:
        return False, None

    is_mobile, os_name = parse_user_agent(user_agent)
    is_blocked = False
    unblock_ts = None

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO security_ips (ip_address, country, city, user_agent, is_mobile, os, first_seen_at, last_seen_at, request_count)
                VALUES (%s, %s, %s, %s, %s, %s, (NOW() AT TIME ZONE 'America/Santiago'), (NOW() AT TIME ZONE 'America/Santiago'), 1)
                ON CONFLICT (ip_address) DO UPDATE SET
                    last_seen_at = (NOW() AT TIME ZONE 'America/Santiago'),
                    request_count = security_ips.request_count + 1,
                    user_agent = COALESCE(NULLIF(EXCLUDED.user_agent, ''), security_ips.user_agent),
                    country = COALESCE(NULLIF(EXCLUDED.country, 'Unknown'), security_ips.country),
                    city = COALESCE(NULLIF(EXCLUDED.city, 'Unknown'), security_ips.city)
                RETURNING is_blocked, blocked_until;
            """, (ip, country or "CL", city or "Unknown", user_agent or "", is_mobile, os_name))

            row = cur.fetchone()
            if row:
                blocked_flag, blocked_until = row
                if blocked_flag and blocked_until:
                    now_santiago = datetime.now(SANTIAGO_TZ).replace(tzinfo=None)
                    if blocked_until > now_santiago:
                        is_blocked = True
                        unblock_ts = blocked_until.replace(tzinfo=SANTIAGO_TZ).timestamp()
                    else:
                        is_blocked = False
        conn.commit()
    except Exception as e:
        logger.error(f"[DB RECORD VISIT ERROR] {e}")
    finally:
        conn.close()

    return is_blocked, unblock_ts

def block_ip(ip: str, hours: int = 1, reason: str = "RATE_LIMIT_EXCEEDED") -> Optional[float]:
    """Registra y persiste el bloqueo de una IP en Supabase con fecha de expiracion en horario Santiago."""
    conn = _get_connection()
    if not conn:
        return None
    unblock_ts = None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO security_ips (ip_address, is_blocked, blocked_until, block_reason, first_seen_at, last_seen_at, request_count)
                VALUES (%s, TRUE, (NOW() AT TIME ZONE 'America/Santiago') + (%s * INTERVAL '1 hour'), %s, (NOW() AT TIME ZONE 'America/Santiago'), (NOW() AT TIME ZONE 'America/Santiago'), 1)
                ON CONFLICT (ip_address) DO UPDATE SET
                    is_blocked = TRUE,
                    blocked_until = (NOW() AT TIME ZONE 'America/Santiago') + (%s * INTERVAL '1 hour'),
                    block_reason = EXCLUDED.block_reason,
                    last_seen_at = (NOW() AT TIME ZONE 'America/Santiago')
                RETURNING blocked_until;
            """, (ip, hours, reason, hours))
            row = cur.fetchone()
            if row and row[0]:
                unblock_ts = row[0].replace(tzinfo=SANTIAGO_TZ).timestamp()
        conn.commit()
    except Exception as e:
        logger.error(f"[DB BLOCK IP ERROR] {e}")
    finally:
        conn.close()
    return unblock_ts

def get_active_blocked_ips() -> Dict[str, float]:
    """Recupera todas las IPs actualmente bloqueadas y sus timestamps de desbloqueo desde Supabase en horario Santiago."""
    conn = _get_connection()
    if not conn:
        return {}
    blocked_dict = {}
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ip_address, blocked_until
                FROM security_ips
                WHERE is_blocked = TRUE AND blocked_until > (NOW() AT TIME ZONE 'America/Santiago');
            """)
            for ip, until in cur.fetchall():
                if until:
                    blocked_dict[ip] = until.replace(tzinfo=SANTIAGO_TZ).timestamp()
    except Exception as e:
        logger.error(f"[DB GET BLOCKED IPS ERROR] {e}")
    finally:
        conn.close()
    return blocked_dict

def unblock_ip(ip: str) -> bool:
    """Desbloquea una IP en Supabase limpiando su estado de bloqueo y contador."""
    conn = _get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE security_ips
                SET is_blocked = FALSE, blocked_until = NULL, block_reason = NULL, request_count = 0
                WHERE ip_address = %s;
            """, (ip,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"[DB UNBLOCK IP ERROR] {e}")
        return False
    finally:
        conn.close()


def normalize_medicine_term(term: str) -> str:
    """Normaliza el termino del medicamento: minusculas, sin espacios multiples, sin tildes ni puntuacion extra."""
    if not term:
        return ""
    s = term.strip().lower()
    s = re.sub(r'\s+', ' ', s)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.strip(" .,;:-")

def upsert_canasta_medicamento(
    term: str,
    results_list: List[Dict[str, Any]],
    display_name: Optional[str] = None
) -> bool:
    """
    Inserta o actualiza un medicamento en canasta_medicamentos.
    Guarda el ultimo JSON de resultados, recalcula precios y suma al contador de busquedas.
    """
    conn = _get_connection()
    if not conn:
        return False

    norm = normalize_medicine_term(term)
    if not norm:
        conn.close()
        return False

    disp = (display_name or term).strip()

    valid_prices = []
    cheapest_pharm = None
    min_p = None
    max_p = None

    for item in results_list:
        p_str = item.get("precio", "")
        p_digits = "".join(c for c in str(p_str) if c.isdigit())
        if p_digits:
            val = int(p_digits)
            if val > 0:
                valid_prices.append((val, item.get("fuente")))

    if valid_prices:
        min_p = min(p[0] for p in valid_prices)
        max_p = max(p[0] for p in valid_prices)
        cheapest_pharm = next((p[1] for p in valid_prices if p[0] == min_p), None)

    total = len(results_list)

    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO canasta_medicamentos (
                    normalized_name, display_name, results_json, total_results,
                    min_price, max_price, cheapest_pharmacy, search_count, first_searched_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, (NOW() AT TIME ZONE 'America/Santiago'), (NOW() AT TIME ZONE 'America/Santiago'))
                ON CONFLICT (normalized_name) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    results_json = CASE WHEN EXCLUDED.total_results > 0 THEN EXCLUDED.results_json ELSE canasta_medicamentos.results_json END,
                    total_results = CASE WHEN EXCLUDED.total_results > 0 THEN EXCLUDED.total_results ELSE canasta_medicamentos.total_results END,
                    min_price = CASE WHEN EXCLUDED.total_results > 0 THEN EXCLUDED.min_price ELSE canasta_medicamentos.min_price END,
                    max_price = CASE WHEN EXCLUDED.total_results > 0 THEN EXCLUDED.max_price ELSE canasta_medicamentos.max_price END,
                    cheapest_pharmacy = CASE WHEN EXCLUDED.total_results > 0 THEN EXCLUDED.cheapest_pharmacy ELSE canasta_medicamentos.cheapest_pharmacy END,
                    search_count = canasta_medicamentos.search_count + 1,
                    updated_at = (NOW() AT TIME ZONE 'America/Santiago');
            """, (
                norm, disp, Json(results_list), total, min_p, max_p, cheapest_pharm
            ))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"[DB CANASTA UPSERT ERROR] {e}")
        return False
    finally:
        conn.close()

def save_recipe_to_canasta(receta_results: List[Dict[str, Any]]):
    """Procesa cada medicamento de la receta y lo guarda/actualiza individualmente en canasta_medicamentos."""
    for item in receta_results:
        if isinstance(item, dict):
            term = item.get("producto")
            results = item.get("resultados", [])
            if term:
                upsert_canasta_medicamento(term, results)


def log_search(
    ip: str,
    raw_query: str,
    is_cached: bool = False,
    response_time_ms: int = 0,
    status: str = "SUCCESS",
    cheapest_pharmacy: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    session_id: Optional[str] = None,
    total_results: int = 0,
    raw_products_json: Optional[Any] = None,
    output_json: Optional[Any] = None
):
    """Guarda un registro de la busqueda en search_logs con sus resultados crudos y el output limpio entregado al cliente."""
    conn = _get_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO search_logs (
                    session_id, ip_address, raw_query, is_cached, 
                    response_time_ms, status, cheapest_pharmacy, min_price, max_price,
                    total_results, raw_products_json, output_json, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, (NOW() AT TIME ZONE 'America/Santiago'));
            """, (
                session_id, ip, raw_query, is_cached,
                response_time_ms, status, cheapest_pharmacy, min_price, max_price,
                total_results,
                Json(raw_products_json) if raw_products_json is not None else None,
                Json(output_json) if output_json is not None else None
            ))
        conn.commit()
    except Exception as e:
        logger.error(f"[DB LOG SEARCH ERROR] {e}")
    finally:
        conn.close()


def get_cached_search(search_term: str) -> Optional[List[Dict[str, Any]]]:
    """
    Recupera los productos crudos cacheados desde search_logs si la busqueda
    fue exitosa y tiene menos de 24 horas de antiguedad.
    """
    conn = _get_connection()
    if not conn:
        return None
        
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT raw_products_json
                FROM search_logs
                WHERE LOWER(raw_query) = LOWER(%s)
                  AND status = 'SUCCESS'
                  AND raw_products_json IS NOT NULL
                  AND created_at > (NOW() AT TIME ZONE 'America/Santiago') - INTERVAL '24 hours'
                ORDER BY created_at DESC
                LIMIT 1;
            """, (search_term.strip(),))
            
            row = cur.fetchone()
            if row and row[0]:
                data = row[0]
                if isinstance(data, list):
                    if data and isinstance(data[0], dict) and "resultados" in data[0]:
                        prods = []
                        for item in data:
                            prods.extend(item.get("resultados", []))
                        return prods
                    return data
                elif isinstance(data, dict):
                    return data.get("resultados", [])
    except Exception as e:
        logger.error(f"[DB GET CACHED SEARCH ERROR] {e}")
    finally:
        conn.close()
        
    return None

def get_pharmacy_cached_scrapes(search_term: str) -> List[Dict[str, Any]]:
    """Compatibilidad: redirige la busqueda de cache a search_logs."""
    res = get_cached_search(search_term)
    return res if res else []

def save_pharmacy_scrape(search_term: str, pharmacy: str, products: List[Dict[str, Any]], ttl_hours: int = 24):
    """Obsoleto: todos los resultados se consolidan directamente en search_logs.raw_products_json."""
    pass


def record_click(*args, **kwargs):
    """Desactivado temporalmente para no consumir procesos."""
    pass


