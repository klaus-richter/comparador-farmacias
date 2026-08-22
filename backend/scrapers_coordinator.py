import asyncio
import time
from typing import List, Dict, Any, Tuple
from playwright.async_api import async_playwright
from backend.scrapers.ecofarmacias import buscar_ecofarmacias

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
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--single-process"
                ]
            )
        return _SHARED_BROWSER

# --- SCRAPERS LIGEROS BASADOS EN PESTAÑAS (PAGES) ---

async def _scrape_page_ahumada(page, producto: str) -> List[Dict[str, Any]]:
    url = f"https://www.farmaciasahumada.cl/search?q={producto}&search-button=&lang=default"
    await page.goto(url, wait_until="domcontentloaded", timeout=12000)
    try:
        await page.wait_for_selector('.product-tile', timeout=3500)
    except:
        pass
    items = await page.evaluate('''() => {
        const results = [];
        const tiles = document.querySelectorAll('.product-grid .product-tile, .product-tile');
        for (const t of tiles) {
            if (t.closest('.carousel, [class*="recommendation"], [class*="sponsored"]')) continue;
            const nameEl = t.querySelector('.pdp-link a');
            const linkEl = t.querySelector('.pdp-link a, a[href*=".html"]');
            const href = linkEl ? linkEl.getAttribute('href') : '';
            let name = nameEl ? nameEl.innerText.trim() : '';
            if (!name && href) {
                const m = href.match(/\\/([a-zA-Z0-9\\-]+)-\\d+\\.html/);
                if (m) name = m[1].replace(/-/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
            }
            const salesEl = t.querySelector('.sales .value, .price .value, .sales, .price');
            const priceText = salesEl ? salesEl.innerText.trim() : '';
            if (name && priceText) {
                const fullHref = href ? (href.startsWith('http') ? href : `https://www.farmaciasahumada.cl${href.startsWith('/') ? '' : '/'}${href}`) : '';
                results.push({ nombre: name, precio: priceText, url: fullHref, fuente: "Farmacias Ahumada", disponible: true });
            }
        }
        return results;
    }''')
    return items[:6]

async def _scrape_page_salcobrand(page, producto: str) -> List[Dict[str, Any]]:
    url = f"https://salcobrand.cl/search_result?query={producto}"
    await page.goto(url, wait_until="domcontentloaded", timeout=12000)
    try:
        await page.wait_for_selector('.product-info, .product-name', timeout=3500)
    except:
        pass
    items = await page.evaluate('''() => {
        const results = [];
        const nodes = document.querySelectorAll('.product-info, .product-item, .product');
        for (const node of nodes) {
            const brandEl = node.querySelector('.product-name, [class*="brand"]');
            const infoEl = node.querySelector('.product-info, [class*="name"], h3, a');
            const brand = brandEl ? brandEl.innerText.trim() : '';
            const info = infoEl ? infoEl.innerText.trim() : '';
            const name = (brand && !info.toLowerCase().includes(brand.toLowerCase())) ? `${brand} - ${info}` : (info || brand);
            const priceEl = node.querySelector('.display-offer-price, .display-secoundary-price-normal, .price');
            const priceText = priceEl ? priceEl.innerText.trim() : '';
            const linkEl = node.querySelector('a');
            const href = linkEl ? linkEl.getAttribute('href') : '';
            if (name && priceText) {
                const fullHref = href ? (href.startsWith('http') ? href : `https://salcobrand.cl${href.startsWith('/') ? '' : '/'}${href}`) : '';
                results.push({ nombre: name, precio: priceText, url: fullHref, fuente: "Salcobrand", disponible: true });
            }
        }
        return results;
    }''')
    return items[:6]

async def _scrape_page_drsimi(page, producto: str) -> List[Dict[str, Any]]:
    url = f"https://www.drsimi.cl/{producto}?_q={producto}&map=ft"
    await page.goto(url, wait_until="domcontentloaded", timeout=12000)
    try:
        await page.wait_for_selector('.vtex-product-summary-2-x-container, [class*="product-summary"]', timeout=3500)
    except:
        pass
    items = await page.evaluate('''() => {
        const results = [];
        const cards = document.querySelectorAll('.vtex-product-summary-2-x-container, [class*="product-summary"], article');
        for (const c of cards) {
            const cardText = c.innerText || '';
            if (/agotado|sin\\s*stock|sin\\s*existencia|no\\s*disponible/i.test(cardText)) continue;

            const brandEl = c.querySelector('[class*="productBrand"], span[class*="brand"]');
            const nameEl = c.querySelector('[class*="productName"], [class*="product-name"], h3, a');
            const brand = brandEl ? brandEl.innerText.trim() : '';
            const nameOnly = nameEl ? nameEl.innerText.trim() : '';
            const fullName = (brand && nameOnly && !nameOnly.toLowerCase().includes(brand.toLowerCase())) ? `${brand} - ${nameOnly}` : (nameOnly || brand);
            
            // Ignorar banners promocionales que no son medicamentos (ej: Club de amigos)
            if (/club de amigos|catalogo|promocion/i.test(fullName)) continue;

            const priceEl = c.querySelector('[class*="sellingPriceValue"], [class*="currencyContainer"], [class*="price_"], [class*="sellingPrice"]');
            const priceText = priceEl ? priceEl.innerText.trim() : '';
            const linkEl = c.querySelector('a');
            const href = linkEl ? linkEl.getAttribute('href') : '';
            if (priceText && fullName) {
                const fullHref = href ? (href.startsWith('http') ? href : `https://www.drsimi.cl${href.startsWith('/') ? '' : '/'}${href}`) : '';
                results.push({ nombre: fullName, precio: priceText, url: fullHref, fuente: "Dr. Simi", disponible: true });
            }
        }
        return results;
    }''')
    return items[:6]

async def _scrape_page_cruzverde(page, producto: str) -> List[Dict[str, Any]]:
    url = f"https://www.cruzverde.cl/search?query={producto}"
    await page.goto(url, wait_until="domcontentloaded", timeout=12000)
    try:
        await page.wait_for_selector('a[href*=".html"]', timeout=3500)
    except:
        pass
    items = await page.evaluate('''() => {
        const results = [];
        const links = Array.from(document.querySelectorAll('a[href*=".html"]'));
        for (const link of links) {
            const card = link.closest('div[class*="flex-col"], [class*="product"], [class*="card"]') || link.parentElement;
            const text = (card ? card.innerText : link.innerText).trim();
            const prices = text.match(/\\$\\s*[\\d\\.]+/g);
            const href = link.getAttribute('href') || '';
            if (prices && prices.length > 0 && href && !results.some(r => r.url === href)) {
                let name = (link.innerText || '').trim();
                if (!name) {
                    const slugMatch = href.match(/\\/([a-zA-Z0-9\\-]+)\\/\\d+\\.html/);
                    if (slugMatch) {
                        name = slugMatch[1].replace(/-/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                    }
                }
                const fullHref = href.startsWith('http') ? href : `https://www.cruzverde.cl${href.startsWith('/') ? '' : '/'}${href}`;
                if (name) {
                    results.push({ nombre: name, precio: prices[prices.length - 1], url: fullHref, fuente: "Cruz Verde", disponible: true });
                }
            }
        }
        return results;
    }''')
    return items[:6]

# --- COORDINADOR PRINCIPAL ULTRA RÁPIDO ---

async def scrapear_todas_las_farmacias(producto: str, max_retries: int = 1) -> Dict[str, Any]:
    """
    Coordina la búsqueda en las 5 farmacias simultáneas usando 1 solo navegador compartido.
    Tiempos récord de 6 a 8 segundos para medicamentos nuevos.
    """
    t0 = time.time()
    browser = await get_shared_browser()
    
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800}
    )

    async def _run_scraper(nombre: str, fn):
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

    # Lanzar las 5 consultas en paralelo real
    respuestas = await asyncio.gather(
        _run_eco(),
        _run_scraper("Farmacias Ahumada", _scrape_page_ahumada),
        _run_scraper("Salcobrand", _scrape_page_salcobrand),
        _run_scraper("Dr. Simi", _scrape_page_drsimi),
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

