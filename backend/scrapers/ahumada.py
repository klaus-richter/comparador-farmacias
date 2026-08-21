import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.farmaciasahumada.cl"

async def buscar_ahumada(producto: str, max_resultados: int = 6) -> list[dict]:
    """
    Busca un producto en Farmacias Ahumada.
    Retorna lista de diccionarios con nombre, precio, url, disponible, fuente.
    """
    url = f"{BASE_URL}/search?q={producto}&search-button=&lang=default"
    resultados = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)

            items_data = await page.evaluate('''() => {
                const results = [];
                // Buscar solo en la grilla de resultados de búsqueda, ignorando carruseles recomendados
                const grid = document.querySelector('.product-grid, .search-results') || document;
                const tiles = grid.querySelectorAll('.product-tile');
                for (const t of tiles) {
                    if (t.closest('.carousel, [class*="recommendation"], [class*="sponsored"]')) continue;
                    
                    const nameEl = t.querySelector('.pdp-link a');
                    const linkEl = t.querySelector('.pdp-link a, a[href*=".html"]');
                    const href = linkEl ? linkEl.getAttribute('href') : '';
                    
                    let name = nameEl ? nameEl.innerText.trim() : '';
                    if (!name && href) {
                        const slugMatch = href.match(/\\/([a-zA-Z0-9\\-]+)-\\d+\\.html/);
                        if (slugMatch) {
                            name = slugMatch[1].replace(/-/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                        }
                    }

                    const salesEl = t.querySelector('.sales .value, .price .value, .sales, .price');
                    const text = t.innerText || '';
                    const prices = text.match(/\\$\\s*[\\d\\.]+/g);
                    const priceText = salesEl ? salesEl.innerText.trim() : (prices && prices.length > 0 ? prices[0] : '');

                    if (name && priceText) {
                        const fullHref = href ? (href.startsWith('http') ? href : `https://www.farmaciasahumada.cl${href.startsWith('/') ? '' : '/'}${href}`) : '';
                        if (!results.some(r => r.name === name && r.href === fullHref)) {
                            results.push({
                                name,
                                priceText,
                                href: fullHref
                            });
                        }
                    }
                }
                return results;
            }''')

            for item in items_data[:max_resultados]:
                m = re.search(r'\$\s*[\d\.]+', item["priceText"])
                precio = m.group(0).replace(" ", "") if m else item["priceText"]

                resultados.append({
                    "nombre": item["name"],
                    "precio": precio,
                    "url": item["href"] or url,
                    "disponible": bool(m),
                    "fuente": "Farmacias Ahumada",
                })

            await browser.close()
    except Exception as e:
        print(f"Error en scraper Ahumada: {e}")

    return resultados
