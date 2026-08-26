import os
import json
import time
from datetime import datetime, time as dtime
import sqlite3
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "cache.db")

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

SEED_PATH = os.path.join(os.path.dirname(__file__), "data", "catalog_seed.json")

def init_db():
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                query TEXT PRIMARY KEY,
                data_json TEXT NOT NULL,
                total INTEGER NOT NULL,
                fecha_ingesta TEXT,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL
            )
        """)
        cursor = conn.execute("PRAGMA table_info(search_cache)")
        cols = [row[1] for row in cursor.fetchall()]
        if "fecha_ingesta" not in cols:
            conn.execute("ALTER TABLE search_cache ADD COLUMN fecha_ingesta TEXT")
        conn.commit()

        # Cargar/Actualizar seed siempre con la versión más completa y fresca
        if os.path.exists(SEED_PATH):
            try:
                with open(SEED_PATH, "r", encoding="utf-8") as f:
                    seed_data = json.load(f)
                for item in seed_data:
                    conn.execute("""
                        INSERT INTO search_cache (query, data_json, total, fecha_ingesta, created_at, expires_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ON CONFLICT(query) DO UPDATE SET
                            data_json = excluded.data_json,
                            total = excluded.total,
                            fecha_ingesta = excluded.fecha_ingesta,
                            created_at = excluded.created_at
                        WHERE excluded.total >= search_cache.total OR search_cache.total = 0
                    """, (
                        item["query"],
                        item["data_json"],
                        item["total"],
                        item.get("fecha_ingesta"),
                        item.get("created_at", time.time()),
                        item.get("expires_at", time.time() + 86400 * 365)
                    ))
                conn.commit()
            except Exception as e:
                print(f"[CACHE SEED ERROR] {e}")


# Inicializar BD al importar
init_db()


import unicodedata
import re

def _normalize_query(query: str) -> str:
    """
    Homologa y normaliza el texto eliminando:
    - Tildes y diacríticos (á -> a, é -> e, í -> i, ó -> o, ú -> u, ñ -> n opcionalmente o conservada)
    - Mayúsculas/minúsculas
    - Espacios dobles o laterales
    """
    text = (query or "").strip().lower()
    # Descomponer caracteres con tildes y remover la marca de acento
    nfkd_form = unicodedata.normalize('NFD', text)
    text = "".join([c for c in nfkd_form if unicodedata.category(c) != 'Mn'])
    # Normalizar espacios múltiples
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def _get_end_of_legal_day_timestamp() -> float:
    """Calcula el timestamp Unix del final del día legal actual (23:59:59 local)."""
    now = datetime.now()
    end_of_day = datetime.combine(now.date(), dtime(23, 59, 59))
    return end_of_day.timestamp()

import difflib

def get_cached_results(query: str) -> Optional[Dict[str, Any]]:
    """
    Retorna el resultado disponible en la base de datos para este medicamento.
    Incluye auto-corrección difusa con difflib (>85% similitud) para tolerar errores tipográficos en 0.001s.
    """
    norm_query = _normalize_query(query)
    try:
        with _get_connection() as conn:
            # 1. Intento de coincidencia exacta
            cursor = conn.execute(
                "SELECT data_json, total, fecha_ingesta, created_at, expires_at FROM search_cache WHERE query = ? AND total > 0",
                (norm_query,)
            )
            row = cursor.fetchone()
            
            # 2. Intento de auto-corrección por prefijo/contención
            if not row and len(norm_query) >= 4:
                cursor = conn.execute(
                    "SELECT data_json, total, fecha_ingesta, created_at, expires_at FROM search_cache WHERE total > 0 AND (query LIKE ? OR ? LIKE query || '%') ORDER BY total DESC LIMIT 1",
                    (f"{norm_query}%", norm_query)
                )
                row = cursor.fetchone()

            # 3. Intento de auto-corrección fonética (i <-> y, b <-> v, z <-> s) y difusa con difflib (cutoff 0.88)
            if not row and len(norm_query) >= 4:
                cursor = conn.execute("SELECT query FROM search_cache WHERE total > 0")
                all_queries = [r[0] for r in cursor.fetchall()]
                matches = []

                # 3a. Coincidencia fonética directa (ej: avamis <-> avamys)
                norm_phonetic = norm_query.replace('y', 'i').replace('b', 'v').replace('z', 's')
                for cand in all_queries:
                    cand_phonetic = cand.replace('y', 'i').replace('b', 'v').replace('z', 's')
                    if norm_phonetic == cand_phonetic:
                        matches = [cand]
                        break

                # 3b. Coincidencia difusa estricta al 88% (evita confusiones de medicamentos LASA)
                if not matches:
                    matches = difflib.get_close_matches(norm_query, all_queries, n=1, cutoff=0.88)


                if matches:
                    cursor = conn.execute(
                        "SELECT data_json, total, fecha_ingesta, created_at, expires_at FROM search_cache WHERE query = ?",
                        (matches[0],)
                    )
                    row = cursor.fetchone()



            if row:
                data = json.loads(row["data_json"])
                return {
                    "producto": query,
                    "total": row["total"],
                    "resultados": data.get("resultados", []),
                    "cobertura": data.get("cobertura", {}),
                    "cached": True,
                    "fecha_ingesta": row["fecha_ingesta"] or datetime.fromtimestamp(row["created_at"]).isoformat(),
                    "created_at": row["created_at"],
                    "expires_at": row["expires_at"]
                }
    except Exception as e:
        print(f"Error leyendo cache para '{query}': {e}")
    return None



def save_cached_results(query: str, data: Dict[str, Any], custom_expires_at: Optional[float] = None):
    """
    Guarda o actualiza los resultados con fecha de ingesta y cobertura de farmacias de forma permanente.
    """
    norm_query = _normalize_query(query)
    now = time.time()
    iso_now = datetime.now().isoformat()
    expires_at = custom_expires_at if custom_expires_at else (now + 86400 * 365) # Persistente
    
    raw_results: List[Dict[str, Any]] = data.get("resultados", [])
    clean_results = []
    for item in raw_results:
        clean_item = {
            "nombre": item.get("nombre", "Medicamento"),
            "precio": item.get("precio", "Consultar"),
            "url": item.get("url", ""),
            "fuente": item.get("fuente", "Desconocida"),
            "disponible": item.get("disponible", True),
            "fecha_ingesta": item.get("fecha_ingesta", iso_now)
        }
        clean_results.append(clean_item)

    total = len(clean_results)
    cobertura = data.get("cobertura", {})
    
    payload = json.dumps({
        "resultados": clean_results,
        "cobertura": cobertura
    }, ensure_ascii=False)
    
    try:
        with _get_connection() as conn:
            conn.execute("""
                INSERT INTO search_cache (query, data_json, total, fecha_ingesta, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(query) DO UPDATE SET
                    data_json=excluded.data_json,
                    total=excluded.total,
                    fecha_ingesta=excluded.fecha_ingesta,
                    created_at=excluded.created_at,
                    expires_at=excluded.expires_at
            """, (norm_query, payload, total, iso_now, now, expires_at))
            conn.commit()
            
            # Sincronización en caliente y en segundo plano a GitHub (si hay token disponible)
            if total > 0:
                try:
                    from backend.github_sync import sync_new_medication_to_github
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(sync_new_medication_to_github(norm_query, payload, total, iso_now))
                    except RuntimeError:
                        pass
                except ImportError:
                    pass
    except Exception as e:
        print(f"Error guardando cache para '{query}': {e}")


def get_all_known_queries() -> List[str]:
    """Retorna la lista de todos los medicamentos alguna vez buscados o registrados."""
    try:
        with _get_connection() as conn:
            return [row[0] for row in conn.execute("SELECT query FROM search_cache ORDER BY query ASC").fetchall()]
    except Exception as e:
        print(f"Error obteniendo catalogo de medicamentos: {e}")
        return []

def clear_expired() -> int:
    """Mantenimiento preventivo (no borra registros vigentes acumulativos)."""
    return 0

def get_cache_stats() -> Dict[str, Any]:
    """Retorna estadísticas completas de la base SQLite acumulativa."""
    try:
        with _get_connection() as conn:
            total_entries = conn.execute("SELECT COUNT(*) FROM search_cache").fetchone()[0]
            queries = [row[0] for row in conn.execute("SELECT query FROM search_cache ORDER BY query ASC").fetchall()]
            return {
                "total_entries": total_entries,
                "cached_queries_count": len(queries),
                "cached_queries": queries,
                "db_path": DB_PATH
            }
    except Exception as e:
        return {"error": str(e)}


def increment_and_get_visits() -> int:
    try:
        with _get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS site_stats (
                    key TEXT PRIMARY KEY,
                    value INTEGER DEFAULT 0
                )
            """)
            conn.execute("INSERT OR IGNORE INTO site_stats (key, value) VALUES ('visits', 0)")
            conn.execute("UPDATE site_stats SET value = value + 1 WHERE key = 'visits'")
            conn.commit()
            cursor = conn.execute("SELECT value FROM site_stats WHERE key = 'visits'")
            row = cursor.fetchone()
            return row[0] if row else 1
    except Exception as e:
        print(f"Error registrando visita: {e}")
        return 1
