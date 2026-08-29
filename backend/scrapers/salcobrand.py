import os
import json
import asyncio
import urllib.request
import urllib.parse
from typing import List, Dict, Any

APP_ID = "GM3RP06HJG"
API_KEY = "0259fe250b3be4b1326eb85e47aa7d81"
INDEX = "sb_variant_production"

def _get_opener():
    proxy_server = os.getenv("PROXY_SERVER")
    proxy_user = os.getenv("PROXY_USERNAME")
    proxy_pass = os.getenv("PROXY_PASSWORD")

    if proxy_server and proxy_user and proxy_pass:
        try:
            parsed = urllib.parse.urlparse(proxy_server)
            auth_url = f"http://{proxy_user}:{proxy_pass}@{parsed.hostname}:{parsed.port}"
            proxy_handler = urllib.request.ProxyHandler({'http': auth_url, 'https': auth_url})
            return urllib.request.build_opener(proxy_handler)
        except Exception:
            return None
    return None

async def buscar_salcobrand(producto: str, max_resultados: int = 20) -> List[Dict[str, Any]]:
    """
    Busca medicamentos en el catálogo oficial de Salcobrand vía su endpoint Algolia CDN
    enrutado a través de IP residencial chilena (IPRoyal) para anonimato total.
    """
    def _do_search():
        url = f"https://{APP_ID}-dsn.algolia.net/1/indexes/*/queries"
        payload = json.dumps({
            "requests": [
                {
                    "indexName": INDEX,
                    "params": f"query={producto}&hitsPerPage={max_resultados}&facets=*&clickAnalytics=true"
                }
            ]
        }).encode('utf-8')
        
        headers = {
            "X-Algolia-Application-Id": APP_ID,
            "X-Algolia-API-Key": API_KEY,
            "Content-Type": "application/json",
            "Referer": "https://salcobrand.cl/search_result",
            "Origin": "https://salcobrand.cl",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
        }
        
        req = urllib.request.Request(url, data=payload, headers=headers)
        opener = _get_opener()
        
        try:
            if opener:
                with opener.open(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
            else:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    
            results = data.get("results", [])
            items = []
            if results:
                hits = results[0].get("hits", [])
                for h in hits:
                    name = h.get("name") or h.get("product_name") or h.get("title")
                    price = h.get("normal_price") or h.get("price") or h.get("final_price") or 0
                    slug = h.get("slug") or h.get("sku") or h.get("objectID")
                    in_stock = h.get("in_stock", True)
                    
                    if name and price and in_stock:
                        price_formatted = f"${price:,.0f}".replace(",", ".")
                        full_url = f"https://salcobrand.cl/products/{slug}"
                        items.append({
                            "nombre": name,
                            "precio": price_formatted,
                            "url": full_url,
                            "fuente": "Salcobrand",
                            "disponible": True
                        })
            return items[:max_resultados]
        except Exception as e:
            print(f"[SALCOBRAND ERROR] {e}")
            return []

    return await asyncio.to_thread(_do_search)
