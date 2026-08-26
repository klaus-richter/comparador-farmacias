import os
import json
import base64
import urllib.request
import urllib.error
import asyncio

REPO = "klaus-richter/comparador-farmacias"
FILE_PATH = "backend/data/catalog_seed.json"
BRANCH = os.getenv("GITHUB_BRANCH", "migration/cloud-run")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

async def sync_new_medication_to_github(query: str, payload_json: str, total: int, fecha_ingesta: str):
    """
    Sincroniza de forma silenciosa en segundo plano un nuevo medicamento al archivo
    backend/data/catalog_seed.json en el repositorio de GitHub.
    """
    token = GITHUB_TOKEN or os.getenv("GITHUB_TOKEN")
    if not token or total <= 0:
        return

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _sync_sync_to_github, query, payload_json, total, fecha_ingesta, token)
    except Exception as e:
        print(f"[GITHUB AUTO-SYNC BACKGROUND ERROR] {e}")

def _sync_sync_to_github(query: str, payload_json: str, total: int, fecha_ingesta: str, token: str):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}?ref={BRANCH}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "comparador-farmacias-autopersist"
    }
    
    # 1. Obtener el catalog_seed.json actual desde GitHub
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            res_data = json.loads(r.read().decode("utf-8"))
            sha = res_data.get("sha")
            raw_content = base64.b64decode(res_data.get("content", "")).decode("utf-8")
            catalog = json.loads(raw_content)
    except Exception as e:
        print(f"[GITHUB AUTO-SYNC] Error leyendo catálogo: {e}")
        return

    # 2. Verificar si ya existe o actualizar
    existing = False
    for item in catalog:
        if item.get("query") == query:
            existing = True
            if total >= item.get("total", 0):
                item["data_json"] = payload_json
                item["total"] = total
                item["fecha_ingesta"] = fecha_ingesta
            break
            
    if not existing:
        catalog.append({
            "query": query,
            "data_json": payload_json,
            "total": total,
            "fecha_ingesta": fecha_ingesta
        })
        print(f"[GITHUB AUTO-SYNC] Agregando nuevo medicamento '{query}' (Total en catálogo: {len(catalog)})")

    # 3. Guardar de vuelta en GitHub
    put_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    put_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "comparador-farmacias-autopersist"
    }
    new_content_b64 = base64.b64encode(json.dumps(catalog, ensure_ascii=False, indent=2).encode("utf-8")).decode("utf-8")
    put_payload = {
        "message": f"🤖 Auto-persist nuevo medicamento '{query}' con {total} opciones [skip ci]",
        "content": new_content_b64,
        "sha": sha,
        "branch": BRANCH
    }
    try:
        put_req = urllib.request.Request(put_url, data=json.dumps(put_payload).encode("utf-8"), headers=put_headers, method="PUT")
        with urllib.request.urlopen(put_req, timeout=15) as r:
            print(f"[GITHUB AUTO-SYNC] Éxito al persistir '{query}' en {BRANCH} (Status {r.status})")
    except Exception as e:
        print(f"[GITHUB AUTO-SYNC] Error guardando en GitHub: {e}")
