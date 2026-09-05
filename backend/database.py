import os
import re
import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta

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
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW(), 1)
                ON CONFLICT (ip_address) DO UPDATE SET
                    last_seen_at = NOW(),
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
                    now_tz = datetime.now(blocked_until.tzinfo)
                    if blocked_until > now_tz:
                        is_blocked = True
                        unblock_ts = blocked_until.timestamp()
                    else:
                        is_blocked = False
        conn.commit()
    except Exception as e:
        logger.error(f"[DB RECORD VISIT ERROR] {e}")
    finally:
        conn.close()

    return is_blocked, unblock_ts

def block_ip(ip: str, hours: int = 1, reason: str = "RATE_LIMIT_EXCEEDED") -> Optional[float]:
    """Registra y persiste el bloqueo de una IP en Supabase con fecha de expiracion."""
    conn = _get_connection()
    if not conn:
        return None
    unblock_ts = None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO security_ips (ip_address, is_blocked, blocked_until, block_reason, first_seen_at, last_seen_at, request_count)
                VALUES (%s, TRUE, NOW() + (%s * INTERVAL '1 hour'), %s, NOW(), NOW(), 1)
                ON CONFLICT (ip_address) DO UPDATE SET
                    is_blocked = TRUE,
                    blocked_until = NOW() + (%s * INTERVAL '1 hour'),
                    block_reason = EXCLUDED.block_reason,
                    last_seen_at = NOW()
                RETURNING blocked_until;
            """, (ip, hours, reason, hours))
            row = cur.fetchone()
            if row and row[0]:
                unblock_ts = row[0].timestamp()
        conn.commit()
    except Exception as e:
        logger.error(f"[DB BLOCK IP ERROR] {e}")
    finally:
        conn.close()
    return unblock_ts

def get_active_blocked_ips() -> Dict[str, float]:
    """Recupera todas las IPs actualmente bloqueadas y sus timestamps de desbloqueo desde Supabase."""
    conn = _get_connection()
    if not conn:
        return {}
    blocked_dict = {}
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ip_address, blocked_until
                FROM security_ips
                WHERE is_blocked = TRUE AND blocked_until > NOW();
            """)
            for ip, until in cur.fetchall():
                if until:
                    blocked_dict[ip] = until.timestamp()
    except Exception as e:
        logger.error(f"[DB GET BLOCKED IPS ERROR] {e}")
    finally:
        conn.close()
    return blocked_dict


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
    raw_products_json: Optional[Any] = None
):
    """Guarda un registro de la busqueda en search_logs con sus resultados crudos en raw_products_json."""
    conn = _get_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO search_logs (
                    session_id, ip_address, raw_query, is_cached, 
                    response_time_ms, status, cheapest_pharmacy, min_price, max_price,
                    total_results, raw_products_json, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
            """, (
                session_id, ip, raw_query, is_cached,
                response_time_ms, status, cheapest_pharmacy, min_price, max_price,
                total_results, Json(raw_products_json) if raw_products_json is not None else None
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
                  AND created_at > NOW() - INTERVAL '24 hours'
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


def record_click(
    medicine: str,
    pharmacy: str,
    price: Optional[str] = None,
    url: Optional[str] = None,
    is_cheapest: bool = False,
    ip: Optional[str] = None
):
    """Registra el clic de compra del usuario hacia una farmacia en user_clicks."""
    conn = _get_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_clicks (medicine, pharmacy, price, url, is_cheapest, ip_address, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW());
            """, (medicine, pharmacy, price, url, is_cheapest, ip))
        conn.commit()
    except Exception as e:
        logger.error(f"[DB RECORD CLICK ERROR] {e}")
    finally:
        conn.close()

