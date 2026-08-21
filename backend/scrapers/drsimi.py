import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.drsimi.cl"

async def buscar_drsimi(producto: str, max_resultados: int = 6) -> list[dict]:
    """
    Busca un producto en Farmacias del Dr. Simi (VTEX).
    """
    url = f"{BASE_URL}/{producto}?_q={producto}&map=ft"
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

            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await page.wait_for_timeout(3000)

            items_data = await page.evaluate('''() => {
                const results = [];
                const cards = document.querySelectorAll('.vtex-product-summary-2-x-container, [class*="product-summary"], article');
                for (const c of cards) {
                    const brandEl = c.querySelector('[class*="productBrand"], span[class*="brand"]');
                    const nameEl = c.querySelector('[class*="productName"], [class*="product-name"], h3, h2, a span');
                    const brand = brandEl ? brandEl.innerText.trim() : '';
                    const nameOnly = nameEl ? nameEl.innerText.trim() : '';
                    const fullName = (brand && nameOnly && !nameOnly.toLowerCase().includes(brand.toLowerCase())) 
                        ? `${brand} - ${nameOnly}` 
                        : (nameOnly || brand || 'Medicamento');

                    const priceEl = c.querySelector('[class*="sellingPriceValue"], [class*="currencyContainer"], [class*="price_"], [class*="sellingPrice"]');
                    const priceText = priceEl ? priceEl.innerText.trim() : (c.innerText.match(/\\$\\s*[\\d\\.]+/)?.[0] || '');

                    const linkEl = c.querySelector('a');
                    const href = linkEl ? linkEl.getAttribute('href') : '';

                    if (priceText && (brand || nameOnly)) {
                        const fullHref = href ? (href.startsWith('http') ? href : `https://www.drsimi.cl${href.startsWith('/') ? '' : '/'}${href}`) : '';
                        if (!results.some(r => r.name === fullName && r.priceText === priceText)) {
                            results.push({ name: fullName, priceText, href: fullHref });
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
                    "fuente": "Dr. Simi",
                })

            await browser.close()
    except Exception as e:
        print(f"Error en scraper Dr. Simi: {e}")

    return resultados
