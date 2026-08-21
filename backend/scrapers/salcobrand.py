import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://salcobrand.cl"

async def buscar_salcobrand(producto: str, max_resultados: int = 6) -> list[dict]:
    """
    Busca un producto en Salcobrand directamente por URL de búsqueda.
    """
    url = f"{BASE_URL}/search_result?query={producto}"
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
            try:
                await page.wait_for_selector('.product-info', timeout=6000)
            except PlaywrightTimeout:
                await page.wait_for_timeout(2000)

            items_data = await page.evaluate("""
                () => {
                    const data = [];
                    const nodes = document.querySelectorAll('.product-info, .product-item, .product, [class*="product-card"]');
                    for (const node of nodes) {
                        const brandEl = node.querySelector('.product-name, [class*="brand"]');
                        const infoEl = node.querySelector('.product-info, [class*="name"], [class*="info"], h3, h2, a');
                        const brand = brandEl ? brandEl.innerText.trim() : '';
                        const info = infoEl ? infoEl.innerText.trim() : '';
                        const name = (brand && !info.toLowerCase().includes(brand.toLowerCase())) ? `${brand} - ${info}` : (info || brand || 'Medicamento');

                        const priceEl = node.querySelector('.display-offer-price, .display-secoundary-price-normal, .price, [class*="price"]');
                        const priceText = priceEl ? priceEl.innerText.trim() : (node.innerText.match(/\\$\\s*[\\d\\.]+/)?.[0] || '');

                        const linkEl = node.querySelector('a');
                        const href = linkEl ? linkEl.getAttribute('href') : '';

                        if (name && priceText) {
                            const fullHref = href ? (href.startsWith('http') ? href : `https://salcobrand.cl${href.startsWith('/') ? '' : '/'}${href}`) : '';
                            if (!data.some(d => d.name === name && d.href === fullHref)) {
                                data.push({ name, priceText, href: fullHref });
                            }
                        }
                    }
                    return data;
                }
            """)

            for item in items_data[:max_resultados]:
                m = re.findall(r'\$\s*[\d\.]+', item["priceText"])
                # Escoger el precio más bajo entre oferta y normal
                precio = m[-1].replace(" ", "") if m else item["priceText"]

                resultados.append({
                    "nombre": item["name"],
                    "precio": precio,
                    "url": item["href"] or url,
                    "disponible": bool(m),
                    "fuente": "Salcobrand",
                })

            await browser.close()
    except Exception as e:
        print(f"Error en scraper Salcobrand: {e}")

    return resultados
