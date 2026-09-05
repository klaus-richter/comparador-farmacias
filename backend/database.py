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

def record_client_visit(ip: str, country: str = "CL", city: str = "Unknown", user_agent: str = "") -> bool:
    """
    Registra o actualiza la visita del cliente en security_ips.
    Retorna True si el cliente esta BLOQUEADO, False si puede continuar.
    """
    conn = _get_connection()
    if not conn:
        return False
        
    is_mobile, os_name = parse_user_agent(user_agent)
    is_blocked = False
    
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
                if blocked_flag:
                    if blocked_until and blocked_until < datetime.now(blocked_until.tzinfo):
                        # El bloqueo ya expiro
                        is_blocked = False
                    else:
                        is_blocked = True
        conn.commit()
    except Exception as e:
        logger.error(f"[DB RECORD VISIT ERROR] {e}")
    finally:
        conn.close()
        
    return is_blocked

def log_search(
    ip: str,
    raw_query: str,
    is_cached: bool = False,
    response_time_ms: int = 0,
    status: str = "SUCCESS",
    cheapest_pharmacy: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    session_id: Optional[str] = None
):
    """Guarda un registro de la busqueda en search_logs para analitica de mercado."""
    conn = _get_connection()
    if not conn:
        return
        
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO search_logs (
                    session_id, ip_address, raw_query, is_cached, 
                    response_time_ms, status, cheapest_pharmacy, min_price, max_price, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
            """, (
                session_id, ip, raw_query, is_cached,
                response_time_ms, status, cheapest_pharmacy, min_price, max_price
            ))
        conn.commit()
    except Exception as e:
        logger.error(f"[DB LOG SEARCH ERROR] {e}")
    finally:
        conn.close()

def save_pharmacy_scrape(search_term: str, pharmacy: str, products: List[Dict[str, Any]], ttl_hours: int = 24):
    """
    Guarda los resultados crudos de una farmacia en pharmacy_raw_scrapes.
    Alimenta tanto el historico diario de precios como el cache caliente.
    """
    conn = _get_connection()
    if not conn:
        return
        
    now = datetime.now()
    expires_at = now + timedelta(hours=ttl_hours)
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pharmacy_raw_scrapes (
                    search_term, fecha_scrape, hora_inyeccion, pharmacy, 
                    total_products, raw_products_json, scraper_status, expires_at
                )
                VALUES (%s, CURRENT_DATE, NOW(), %s, %s, %s, 'OK', %s)
                ON CONFLICT (search_term, pharmacy, fecha_scrape) DO UPDATE SET
                    hora_inyeccion = NOW(),
                    total_products = EXCLUDED.total_products,
                    raw_products_json = EXCLUDED.raw_products_json,
                    expires_at = EXCLUDED.expires_at
                WHERE EXCLUDED.total_products >= pharmacy_raw_scrapes.total_products OR pharmacy_raw_scrapes.total_products = 0;
            """, (search_term.lower().strip(), pharmacy, len(products), Json(products), expires_at))
        conn.commit()
    except Exception as e:
        logger.error(f"[DB SAVE SCRAPE ERROR] {e}")
    finally:
        conn.close()

def get_pharmacy_cached_scrapes(search_term: str) -> List[Dict[str, Any]]:
    """
    Recupera los productos crudos cacheados de todas las farmacias para un termino,
    siempre y cuando no hayan expirado.
    """
    conn = _get_connection()
    if not conn:
        return []
        
    all_products = []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT pharmacy, raw_products_json
                FROM pharmacy_raw_scrapes
                WHERE search_term = %s AND expires_at > NOW();
            """, (search_term.lower().strip(),))
            
            rows = cur.fetchall()
            for row in rows:
                pharmacy, prods = row
                if isinstance(prods, list):
                    all_products.extend(prods)
    except Exception as e:
        logger.error(f"[DB GET CACHE ERROR] {e}")
    finally:
        conn.close()
        
    return all_products

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

