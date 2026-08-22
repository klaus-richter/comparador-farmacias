import urllib.request
import json
import re

API_URL = "https://search.ecofarmacias.cl/indexes/productos/search"
HEADERS = {
    "authorization": "Bearer 93de875805b42f6801eede3daa68a8f5dc1a5807d665e4ac4faad46308adb4cd",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

async def buscar_ecofarmacias(producto: str, max_resultados: int = 6) -> list[dict]:
    """
    Busca productos en Ecofarmacias a través de su API Meilisearch directa.
    Ultra rápido (~0.1s).
    """
    resultados = []
    try:
        payload = json.dumps({
            "q": producto,
            "limit": max_resultados * 2,
            "offset": 0,
            "attributesToRetrieve": ["id", "name", "url", "price", "sale_price", "regular_price", "in_stock"]
        }).encode("utf-8")

        req = urllib.request.Request(API_URL, data=payload, headers=HEADERS, method="POST")
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            hits = data.get("hits", [])

            for hit in hits:
                # Descartar productos agotados o sin stock / sin existencias
                if hit.get("in_stock") is False:
                    continue

                name = hit.get("name", "").strip()
                # Limpiar tags <mark> si vienen
                name = re.sub(r'</?mark>', '', name)
                
                # Precio: preferir sale_price si existe y es menor, sino price o regular_price
                price_val = hit.get("sale_price") or hit.get("price") or hit.get("regular_price")
                if not price_val:
                    continue

                try:
                    price_int = int(float(price_val))
                    precio_str = f"${price_int:,.0f}".replace(",", ".")
                except Exception:
                    precio_str = str(price_val)

                url = hit.get("url") or f"https://www.ecofarmacias.cl/buscar/?q={urllib.parse.quote(producto)}"

                if name and not any(r["nombre"] == name for r in resultados):
                    resultados.append({
                        "nombre": name,
                        "precio": precio_str,
                        "url": url,
                        "disponible": True,
                        "fuente": "Ecofarmacias"
                    })

                if len(resultados) >= max_resultados:
                    break

    except Exception as e:
        print(f"Error en scraper Ecofarmacias: {e}")

    return resultados
