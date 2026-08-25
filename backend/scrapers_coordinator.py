import asyncio
import time
from typing import List, Dict, Any, Tuple
from playwright.async_api import async_playwright
from backend.scrapers.ecofarmacias import buscar_ecofarmacias

# ── Resource blocking: reduce CPU/RAM/tiempo 40-60% en Render ──
_SKIP_TYPES = {"image","stylesheet","font","media"}
_SKIP_DOMAINS = ["google","facebook","analytics","gtm","clarity","hotjar",
    "doubleclick","datadog","segment","tiktok","twitter",
    "pixel","ads","tracking","newrelic","akamai","omtrdc"]

async def _block_resources(route):
    req = route.request
    if req.resource_type in _SKIP_TYPES:
        await route.abort(); return
    if any(d in req.url.lower() for d in _SKIP_DOMAINS):
        await route.abort(); return
    await route.continue_()



# Instancia global y única de Playwright para todo el servidor
_PLAYWRIGHT_INSTANCE = None
_SHARED_BROWSER = None
_BROWSER_LOCK = asyncio.Lock()

async def get_shared_browser():
    """Obtiene o inicializa un único navegador Chromium en memoria para todo el servidor."""
    global _PLAYWRIGHT_INSTANCE, _SHARED_BROWSER
    async with _BROWSER_LOCK:
        if _SHARED_BROWSER is None or not _SHARED_BROWSER.is_connected():
            if _PLAYWRIGHT_INSTANCE is None:
                _PLAYWRIGHT_INSTANCE = await async_playwright().start()
            _SHARED_BROWSER = await _PLAYWRIGHT_INSTANCE.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-zygote"
                ]
            )
        return _SHARED_BROWSER

# --- SCRAPERS LIGEROS BASADOS EN PESTAÑAS (PAGES) ---

async def _scrape_page_ahumada(page, producto: str) -> List[Dict[str, Any]]:
    url = f"https://www.farmaciasahumada.cl/search?q={producto}&search-button=&lang=default"
    await page.route("**/*", _block_resources)
    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    try:
        await page.wait_for_selector('.product-tile, .pdp-link, a[href*=".html"]', timeout=6000)
    except:
        await page.wait_for_timeout(3000)
    items = await page.evaluate(r"""() => {
        const results = [];
        const tiles = document.querySelectorAll('.product-tile');
        for (const t of tiles) {
            if (t.closest('.carousel, [class*="recommendation"], [class*="sponsored"]')) continue;
            const txt = t.innerText || '';
            if (/agotado|sin\s*stock|sin\s*existencias|no\s*disponible/i.test(txt)) continue;
            const nameEl = t.querySelector('.pdp-link a, .product-name a');
            const linkEl = t.querySelector('.pdp-link a, a[href*=".html"]');
            const href = linkEl ? linkEl.getAttribute('href') : '';
            let name = nameEl ? nameEl.innerText.trim() : '';
            if (!name && href) {
                const m = href.match(/\/([a-zA-Z0-9\-]+)-\d+\.html/);
                if (m) name = m[1].replace(/-/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            }
            const prices = txt.match(/\$\s*[\d\.]+/g);
            if (name && prices && prices.length > 0) {
                // Tomar el precio final limpio (primer match de precio o el más relevante)
                const cleanPrice = prices[0].replace(/\s+/g, '');
                const fullHref = href.startsWith('http') ? href : `https://www.farmaciasahumada.cl${href.startsWith('/') ? '' : '/'}${href}`;
                if (!results.some(x => x.nombre === name)) {
                    results.push({ nombre: name, precio: cleanPrice, url: fullHref, fuente: "Farmacias Ahumada", disponible: true });
                }
            }
        }
        return results.slice(0, 6);
    }""")
    return items


async def _scrape_page_salcobrand(page, producto: str) -> List[Dict[str, Any]]:
    url = f"https://salcobrand.cl/search_result?query={producto}"
    await page.route("**/*", _block_resources)
    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    try:
        await page.wait_for_selector('a[href*="/products/"], .display-offer-price, .product-name', timeout=7000)
    except:
        await page.wait_for_timeout(3500)
    items = await page.evaluate(r"""() => {
        const results = [], seen = new Set();
        const productLinks = document.querySelectorAll('a[href*="/products/"]');
        for (const lk of productLinks) {
            const href = lk.getAttribute('href') || '';
            const card = lk.closest('div[class*="product"], li[class*="product"], div[class*="card"], article') || lk.parentElement;
            const txt = card ? card.innerText.trim() : (lk.innerText || '').trim();
            if (/agotado|sin\s*stock|no\s*disponible/i.test(txt)) continue;

            const prices = txt.match(/\$\s*[\d\.]+/g);
            if (!prices || prices.length === 0) continue;

            const nameEl = card ? card.querySelector('h2, h3, .product-name, [class*="Name"], [class*="name"]') : null;
            const lines = txt.split('\n').map(l => l.trim()).filter(l => l && !l.includes('$') && l.length > 3 && l.length < 90);
            let name = nameEl ? nameEl.innerText.trim() : (lines.length > 0 ? lines[0] : '');

            if (!name) {
                const slugMatch = href.match(/\/products\/([a-zA-Z0-9\-]+)/);
                if (slugMatch) {
                    name = slugMatch[1].replace(/-/g, ' ').toUpperCase();
                }
            }

            if (name && !seen.has(name)) {
                seen.add(name);
                const cleanPrice = prices[0].replace(/\s+/g, '');
                const fullHref = href.startsWith('http') ? href : `https://salcobrand.cl${href.startsWith('/') ? '' : '/'}${href}`;
                results.push({ nombre: name, precio: cleanPrice, url: fullHref, fuente: "Salcobrand", disponible: true });
            }
        }
        return results.slice(0, 6);
    }""")
    return items


async def _fetch_drsimi_vtex(producto: str) -> List[Dict[str, Any]]:
    """Consulta directa a la API REST de catálogo VTEX de Dr. Simi (0 Chromium, ~0.4s)."""
    import urllib.parse
    q_encoded = urllib.parse.quote(producto)
    url = f"https://www.drsimi.cl/api/catalog_system/pub/products/search?ft={q_encoded}&_from=0&_to=6"
    
    def _do_get():
        import urllib.request, json
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json"
        })
        try:
            with urllib.request.urlopen(req, timeout=6) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            return []

    data = await asyncio.to_thread(_do_get)
    results = []
    for p in data:
        name = p.get("productName", "")
        items = p.get("items", [])
        if not items:
            continue
        sellers = items[0].get("sellers", [])
        if not sellers:
            continue
        offer = sellers[0].get("commertialOffer", {})
        price = offer.get("Price", 0)
        avail = offer.get("IsAvailable", False)
        
        # Ignorar no disponibles o banners promocionales
        if not avail or price <= 0 or "club de amigos" in name.lower():
            continue
            
        clean_price = f"${int(price):,}".replace(",", ".")
        link_text = p.get("linkText", "")
        full_href = f"https://www.drsimi.cl/{link_text}/p" if link_text else "https://www.drsimi.cl"
        results.append({
            "nombre": name,
            "precio": clean_price,
            "url": full_href,
            "fuente": "Dr. Simi",
            "disponible": True
        })
    return results[:6]



async def _scrape_page_cruzverde(page, producto: str) -> List[Dict[str, Any]]:
    url = f"https://www.cruzverde.cl/search?query={producto}"
    await page.route("**/*", _block_resources)
    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    try:
        await page.wait_for_selector('a[href*=".html"]', timeout=9000)
    except:
        pass
    await page.wait_for_timeout(2500)

    CV_EVAL = r"""() => {
        const results = [], seen = new Set();
        const links = Array.from(document.querySelectorAll('a[href*=".html"]'));
        for (const a of links) {
            const href = a.getAttribute('href') || '';
            if (!/\/\d+\.html(\?|$)/.test(href) || seen.has(href)) continue;

            // Subir en el árbol DOM hasta encontrar la tarjeta con el precio
            let cur = a;
            let card = null;
            for (let i = 0; i < 6; i++) {
                if (!cur.parentElement) break;
                cur = cur.parentElement;
                if (/\$\s*[\d\.]+/g.test(cur.innerText || '')) {
                    card = cur;
                    break;
                }
            }
            if (!card) continue;
            seen.add(href);

            const txt = card.innerText.trim();
            if (/agotado|sin\s*stock|sin\s*existencia|no\s*disponible/i.test(txt)) continue;

            const prices = txt.match(/\$\s*[\d\.]+/g);
            if (!prices || prices.length === 0) continue;

            // Extraer nombre legible combinando marca o texto relevante
            const lines = txt.split('\n').map(l => l.trim()).filter(l => l && !l.includes('$') && l.length > 2 && l.length < 90 && !/receta|bioequivalente|destacado|oferta/i.test(l));
            let name = lines.length > 1 ? `${lines[0]} - ${lines[1]}` : (lines.length === 1 ? lines[0] : '');

            if (!name) {
                const slugMatch = href.match(/\/([a-zA-Z0-9\-]+)\/\d+\.html/);
                if (slugMatch) {
                    name = slugMatch[1].replace(/--+/g, ' - ').replace(/-/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                }
            }

            const cleanPrice = prices[prices.length - 1].replace(/\s+/g, '');
            const fullHref = href.startsWith('http') ? href : `https://www.cruzverde.cl${href.startsWith('/') ? '' : '/'}${href}`;
            results.push({ nombre: name, precio: cleanPrice, url: fullHref, fuente: "Cruz Verde", disponible: true });
        }
        return results.slice(0, 6);
    }"""

    items = await page.evaluate(CV_EVAL)
    if not items:
        await page.wait_for_timeout(2500)
        items = await page.evaluate(CV_EVAL)
    return items




# Semáforo para controlar concurrencia de pestañas y no saturar los 0.1 CPU de Render
_PAGE_SEMAPHORE = asyncio.Semaphore(1)

# --- COORDINADOR PRINCIPAL ULTRA RÁPIDO ---

async def scrapear_todas_las_farmacias(producto: str, max_retries: int = 1) -> Dict[str, Any]:
    """
    Coordina la búsqueda en las 5 farmacias simultáneas usando 1 solo navegador compartido.
    Usa semáforo para evitar starvation de CPU en contenedores de 0.1 CPU.
    """
    t0 = time.time()
    browser = await get_shared_browser()
    
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800}
    )

    async def _run_scraper(nombre: str, fn):
        async with _PAGE_SEMAPHORE:
            try:
                page = await context.new_page()
                try:
                    items = await fn(page, producto)
                    return nombre, items, {"status": "OK" if items else "SIN_STOCK", "total": len(items)}
                finally:
                    await page.close()
            except Exception as e:
                return nombre, [], {"status": "ERROR", "error": str(e), "total": 0}

    async def _run_eco():
        try:
            items = await buscar_ecofarmacias(producto)
            return "Ecofarmacias", items, {"status": "OK" if items else "SIN_STOCK", "total": len(items)}
        except Exception as e:
            return "Ecofarmacias", [], {"status": "ERROR", "error": str(e), "total": 0}

    async def _run_simi():
        try:
            items = await _fetch_drsimi_vtex(producto)
            return "Dr. Simi", items, {"status": "OK" if items else "SIN_STOCK", "total": len(items)}
        except Exception as e:
            return "Dr. Simi", [], {"status": "ERROR", "error": str(e), "total": 0}

    # Ecofarmacias y Dr. Simi corren en paralelo inmediato por HTTP REST (0 Chromium, <0.8s)
    # Las 3 grandes restantes (Ahumada, Salco, Cruz Verde) usan Chromium con semáforo y resource blocking
    respuestas = await asyncio.gather(
        _run_eco(),
        _run_simi(),
        _run_scraper("Farmacias Ahumada", _scrape_page_ahumada),
        _run_scraper("Salcobrand", _scrape_page_salcobrand),
        _run_scraper("Cruz Verde", _scrape_page_cruzverde),
    )



    await context.close()

    todos_los_resultados = []
    reporte_cobertura = {}

    for nombre, items, diag in respuestas:
        reporte_cobertura[nombre] = diag
        todos_los_resultados.extend(items)

    farmacias_con_stock = sum(1 for d in reporte_cobertura.values() if d["status"] == "OK")
    farmacias_sin_stock = sum(1 for d in reporte_cobertura.values() if d["status"] == "SIN_STOCK")
    farmacias_error = sum(1 for d in reporte_cobertura.values() if d["status"] == "ERROR")

    elapsed = round(time.time() - t0, 2)

    return {
        "producto": producto,
        "total": len(todos_los_resultados),
        "resultados": todos_los_resultados,
        "cobertura": {
            "total_farmacias": 5,
            "con_stock": farmacias_con_stock,
            "sin_stock": farmacias_sin_stock,
            "con_error": farmacias_error,
            "detalle": reporte_cobertura
        },
        "elapsed_seconds": elapsed
    }

async def scrapear_farmacias_especificas(producto: str, nombres_farmacias: List[str], max_retries: int = 1) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Auto-Healing ultrarrápido para farmacias puntuales."""
    t0 = time.time()
    browser = await get_shared_browser()
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800}
    )

    mapping = {
        "Farmacias Ahumada": _scrape_page_ahumada,
        "Salcobrand": _scrape_page_salcobrand,
        "Dr. Simi": _scrape_page_drsimi,
        "Cruz Verde": _scrape_page_cruzverde
    }

    tasks = []
    for nombre, fn in mapping.items():
        if any(n.lower() in nombre.lower() or nombre.lower() in n.lower() for n in nombres_farmacias):
            async def _run(n=nombre, f=fn):
                try:
                    page = await context.new_page()
                    try:
                        items = await f(page, producto)
                        return n, items, {"status": "OK" if items else "SIN_STOCK", "total": len(items)}
                    finally:
                        await page.close()
                except Exception as e:
                    return n, [], {"status": "ERROR", "error": str(e), "total": 0}
            tasks.append(_run())

    if not tasks:
        await context.close()
        return [], {}

    respuestas = await asyncio.gather(*tasks)
    await context.close()

    nuevos_items = []
    nuevo_reporte = {}
    for nombre, items, diag in respuestas:
        nuevo_reporte[nombre] = diag
        nuevos_items.extend(items)

    return nuevos_items, nuevo_reporte

