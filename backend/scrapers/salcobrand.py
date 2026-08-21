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
            try:
                await page.wait_for_selector(".product-info, .product-name", timeout=8000)
            except PlaywrightTimeout:
                await page.wait_for_timeout(2000)

            items_data = await page.evaluate("""
                () => {
                    const data = [];
                    const nodes = document.querySelectorAll('.product-info');
                    for (const node of nodes) {
                        const parent = node.closest('.product, [class*="product-item"], .col-xs-6, .col-sm-4') || node.parentElement.parentElement;
                        if (!parent) continue;

                        const brandEl = parent.querySelector('.product-name');
                        const infoEl = parent.querySelector('.product-info');
                        const brand = brandEl ? brandEl.innerText.trim() : '';
                        const info = infoEl ? infoEl.innerText.trim() : '';

                        // Nombre del producto: combinar marca + info
                        const name = (brand && info && !info.toLowerCase().includes(brand.toLowerCase()))
                            ? `${brand} ${info}`
                            : (info || brand || 'Medicamento');

                        const offerEl = parent.querySelector('.display-offer-price');
                        const normalEl = parent.querySelector('.display-secoundary-price-normal, .price, [class*="price"]');
                        const priceText = (offerEl && offerEl.innerText.trim())
                            ? offerEl.innerText.trim()
                            : (normalEl ? normalEl.innerText.trim() : '');

                        const linkEl = parent.querySelector('a');
                        const href = linkEl ? linkEl.getAttribute('href') : '';

                        if (name && priceText) {
                            const fullHref = href
                                ? (href.startsWith('http') ? href : `https://salcobrand.cl${href.startsWith('/') ? '' : '/'}${href}`)
                                : '';
                            if (!data.some(d => d.name === name && d.href === fullHref)) {
                                data.push({ name, priceText, href: fullHref });
                            }
                        }
                    }
                    return data;
                }
            """)

            for item in items_data[:max_resultados]:
                # El precio de oferta viene primero, luego el normal
                m = re.search(r'\$\s*[\d\.]+', item["priceText"])
                precio = m.group(0).replace(" ", "") if m else item["priceText"]

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
