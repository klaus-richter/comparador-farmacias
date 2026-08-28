import sqlite3
import os
import json
import csv
import io
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "analytics.db")

# Zona horaria de Chile (UTC-3 / UTC-4)
CHILE_TZ = timezone(timedelta(hours=-4))

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_analytics_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Tabla de Búsquedas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analytics_searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora INTEGER NOT NULL,
        dia_semana TEXT NOT NULL,
        query TEXT NOT NULL,
        med_count INTEGER DEFAULT 1,
        elapsed_ms INTEGER DEFAULT 0,
        is_cache INTEGER DEFAULT 0,
        winner_pharmacy TEXT,
        winner_price TEXT,
        coverage_json TEXT,
        zero_count INTEGER DEFAULT 0,
        device_type TEXT
    );
    """)

    # 2. Tabla de Clicks en Botones ↗ de Farmacias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analytics_clicks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora INTEGER NOT NULL,
        medicine TEXT NOT NULL,
        pharmacy TEXT NOT NULL,
        price TEXT,
        url TEXT,
        is_cheapest INTEGER DEFAULT 0
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_searches_fecha ON analytics_searches(fecha);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clicks_fecha ON analytics_clicks(fecha);")
    conn.commit()
    conn.close()

def record_search(query: str, med_count: int = 1, elapsed_ms: int = 0, is_cache: bool = False,
                  winner_pharmacy: str = None, winner_price: str = None, 
                  coverage: dict = None, user_agent: str = ""):
    try:
        now = datetime.now(CHILE_TZ)
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        fecha_str = now.strftime("%Y-%m-%d")
        hora_int = now.hour
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_semana = dias[now.weekday()]

        device = "Mobile" if any(k in (user_agent or "").lower() for k in ["mobi", "android", "iphone"]) else "Desktop"
        
        # Calcular farmacias en 0 (alertas de fallas)
        zero_count = 0
        if isinstance(coverage, dict):
            for f_name, f_data in coverage.items():
                if isinstance(f_data, dict) and f_data.get("status") in ["SIN_STOCK", "ERROR"] and f_data.get("total", 0) == 0:
                    zero_count += 1

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO analytics_searches 
        (timestamp, fecha, hora, dia_semana, query, med_count, elapsed_ms, is_cache, winner_pharmacy, winner_price, coverage_json, zero_count, device_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (now_str, fecha_str, hora_int, dia_semana, query.strip().lower(), med_count, int(elapsed_ms), 1 if is_cache else 0,
              winner_pharmacy, winner_price, json.dumps(coverage or {}), zero_count, device))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error grabando analytics search: {e}")

def record_click(medicine: str, pharmacy: str, price: str = None, url: str = None, is_cheapest: bool = False):
    try:
        now = datetime.now(CHILE_TZ)
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        fecha_str = now.strftime("%Y-%m-%d")
        hora_int = now.hour

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO analytics_clicks (timestamp, fecha, hora, medicine, pharmacy, price, url, is_cheapest)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (now_str, fecha_str, hora_int, (medicine or "").strip(), (pharmacy or "").strip(), price, url, 1 if is_cheapest else 0))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error grabando analytics click: {e}")

def get_top_search_terms_for_cron(limit: int = 25) -> list:
    """Extrae los medicamentos más buscados por usuarios reales para pre-calentar el cron de las 3 AM."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT query, COUNT(*) as total 
        FROM analytics_searches 
        GROUP BY query 
        ORDER BY total DESC 
        LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        # Desglosar recetas compuestas (separadas por coma) en términos individuales
        terms = set()
        for r in rows:
            q = r["query"]
            for part in q.split(","):
                clean = part.strip()
                if len(clean) >= 3:
                    terms.add(clean)
        return list(terms)[:limit]
    except Exception:
        return []

def get_metrics_summary() -> dict:
    """Genera el reporte integral de analítica y salud del comparador."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(CHILE_TZ)
    hoy_str = now.strftime("%Y-%m-%d")
    mes_str = now.strftime("%Y-%m")

    # 1. Totales Generales
    cursor.execute("SELECT COUNT(*) FROM analytics_searches;")
    total_searches = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analytics_searches WHERE fecha = ?;", (hoy_str,))
    searches_today = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analytics_searches WHERE fecha LIKE ?;", (f"{mes_str}%",))
    searches_month = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analytics_clicks;")
    total_clicks = cursor.fetchone()[0]

    # 2. Distribución Horaria (0 a 23 hrs)
    cursor.execute("SELECT hora, COUNT(*) as count FROM analytics_searches GROUP BY hora ORDER BY hora ASC;")
    hours_data = {h: 0 for h in range(24)}
    for r in cursor.fetchall():
        hours_data[r["hora"]] = r["count"]

    sorted_hours = sorted(hours_data.items(), key=lambda x: x[1], reverse=True)
    peak_hours = [f"{h:02d}:00 hrs ({cnt} búsquedas)" for h, cnt in sorted_hours[:3] if cnt > 0]
    off_peak_hours = [f"{h:02d}:00 hrs" for h, cnt in sorted_hours[-4:]]

    # 3. Top Medicamentos Buscados
    cursor.execute("SELECT query, COUNT(*) as cnt FROM analytics_searches GROUP BY query ORDER BY cnt DESC LIMIT 10;")
    top_searches = [{"query": r["query"], "count": r["cnt"]} for r in cursor.fetchall()]

    # 4. Preferencia de Compra (Clicks por Farmacia)
    cursor.execute("SELECT pharmacy, COUNT(*) as cnt FROM analytics_clicks GROUP BY pharmacy ORDER BY cnt DESC;")
    clicks_by_pharmacy = [{"pharmacy": r["pharmacy"], "clicks": r["cnt"]} for r in cursor.fetchall()]

    # 5. Farmacias Ganadoras (#1 Más Baratas)
    cursor.execute("SELECT winner_pharmacy, COUNT(*) as cnt FROM analytics_searches WHERE winner_pharmacy IS NOT NULL GROUP BY winner_pharmacy ORDER BY cnt DESC;")
    winners_rank = [{"pharmacy": r["winner_pharmacy"], "wins": r["cnt"]} for r in cursor.fetchall()]

    # 6. Salud de Scrapers (Fallas de Cero Resultados)
    cursor.execute("SELECT COUNT(*) FROM analytics_searches WHERE zero_count > 0;")
    searches_with_zero = cursor.fetchone()[0]
    health_rate = round(((total_searches - searches_with_zero) / total_searches * 100), 1) if total_searches > 0 else 100.0

    # 7. Dispositivos
    cursor.execute("SELECT device_type, COUNT(*) as cnt FROM analytics_searches GROUP BY device_type;")
    devices = {r["device_type"] or "Desktop": r["cnt"] for r in cursor.fetchall()}

    conn.close()

    return {
        "generales": {
            "total_busquedas": total_searches,
            "busquedas_hoy": searches_today,
            "busquedas_mes": searches_month,
            "total_clicks_compra": total_clicks,
            "tasa_conversion_clicks": f"{(total_clicks / total_searches * 100):.1f}%" if total_searches > 0 else "0%",
            "salud_scrapers_porcentaje": f"{health_rate}%"
        },
        "horarios_chile": {
            "distribucion_24h": hours_data,
            "horas_peak": peak_hours,
            "horas_menor_actividad": off_peak_hours
        },
        "top_busquedas": top_searches,
        "clicks_por_farmacia": clicks_by_pharmacy,
        "farmacias_mas_economicas_ganadas": winners_rank,
        "dispositivos": devices
    }

def export_searches_csv() -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analytics_searches ORDER BY id DESC;")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp (Chile)", "Fecha", "Hora", "Dia", "Receta / Termino", "Cantidad Meds", "Tiempo ms", "Es Cache", "Ganadora", "Precio Ganador", "Fallas Cero", "Dispositivo"])
    for r in rows:
        writer.writerow([r["id"], r["timestamp"], r["fecha"], r["hora"], r["dia_semana"], r["query"], r["med_count"], r["elapsed_ms"], r["is_cache"], r["winner_pharmacy"], r["winner_price"], r["zero_count"], r["device_type"]])
    return output.getvalue()

def export_clicks_csv() -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analytics_clicks ORDER BY id DESC;")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Timestamp (Chile)", "Fecha", "Hora", "Medicamento", "Farmacia Clickeada", "Precio", "URL", "Era el mas barato"])
    for r in rows:
        writer.writerow([r["id"], r["timestamp"], r["fecha"], r["hora"], r["medicine"], r["pharmacy"], r["price"], r["url"], r["is_cheapest"]])
    return output.getvalue()

# Inicializar tablas al importar
init_analytics_db()
