import re
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.cruzverde.cl"

async def buscar_cruzverde(producto: str, max_resultados: int = 5) -> list[dict]:
    """
    Busca un producto en Farmacias Cruz Verde.
    1. Extrae productos desde la vista de búsqueda (fast path si la card tiene precio).
    2. Si la card no incluye el precio o falla el renderizado, navega a la URL del producto para extraer el precio real.
    """
    url = f"{BASE_URL}/search?query={producto}"
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
            try:
                await page.wait_for_selector('a[href*=".html"]', timeout=7000)
            except PlaywrightTimeout:
                await page.wait_for_timeout(2500)

            # Extraer links de productos y precios desde las cards de búsqueda
            products_from_search = await page.evaluate('''() => {
                const results = [];
                const seen = new Set();
                const links = Array.from(document.querySelectorAll('a[href*=".html"]'));

                for (const link of links) {
                    const href = link.getAttribute('href') || '';
                    if (!href || seen.has(href)) continue;
                    // Solo links de productos con formato /slug/12345.html
                    if (!/\\/\\d+\\.html$/.test(href)) continue;
                    seen.add(href);

                    const fullHref = href.startsWith('http') ? href : `https://www.cruzverde.cl${href.startsWith('/') ? '' : '/'}${href}`;

                    // Obtener nombre desde el slug como fallback
                    let slugName = '';
                    const slugMatch = href.match(/\\/([a-zA-Z0-9\\-]+)\\/\\d+\\.html/);
                    if (slugMatch) {
                        slugName = slugMatch[1].replace(/--+/g, ' - ').replace(/-/g, ' ');
                        slugName = slugName.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                    }

                    // Buscar card contenedora
                    const card = link.closest('div[class*="product"], div[class*="card"], div[class*="tile"], div[class*="flex-col"]') || link.parentElement;
                    const cardText = card ? card.innerText.trim() : (link.innerText || '').trim();

                    // Descartar si está agotado o sin existencias
                    if (/agotado|sin\\s*stock|sin\\s*existencia|sin\\s*existencias|no\\s*disponible|out-of-stock/i.test(cardText)) continue;

                    // Extraer precios presentes en el texto del card (mejor precio disponible / oferta $18.421)
                    const prices = cardText.match(/\\$\\s*[\\d\\.]+/g);
                    let priceText = (prices && prices.length > 0) ? prices[prices.length - 1] : '';

                    // Extraer nombre legible
                    const lines = cardText.split('\\n').map(l => l.trim()).filter(Boolean);
                    const brand = lines.length > 0 && !lines[0].includes('$') && lines[0].length < 30 ? lines[0] : '';
                    let finalName = slugName || (lines.find(l => !l.includes('$') && l.length > 3) || 'Medicamento');
                    if (brand && slugName && !slugName.toLowerCase().includes(brand.toLowerCase())) {
                        finalName = `${brand} - ${slugName}`;
                    }

                    results.push({
                        name: finalName,
                        priceText: priceText,
                        href: fullHref
                    });
                }
                return results;
            }''')

            items_to_process = products_from_search[:max_resultados]

            for item in items_to_process:
                name = item["name"]
                price_text = item["priceText"]
                href = item["href"]

                # Si no encontramos precio en la card, hacemos fallback a la página del producto
                if not price_text:
                    try:
                        prod_page = await context.new_page()
                        await prod_page.goto(href, wait_until="domcontentloaded", timeout=12000)
                        try:
                            await prod_page.wait_for_selector('[class*="price"], [class*="Price"], .price, h1', timeout=4000)
                        except PlaywrightTimeout:
                            await prod_page.wait_for_timeout(1500)

                        extracted_price = await prod_page.evaluate('''() => {
                            const selectors = [
                                '[class*="offerPrice"]', '[class*="offer-price"]',
                                '[class*="salePrice"]', '[class*="sale-price"]',
                                '[class*="finalPrice"]', '[class*="price"]',
                                '[class*="Price"]', '.value'
                            ];
                            for (const sel of selectors) {
                                const el = document.querySelector(sel);
                                if (el) {
                                    const text = el.innerText || '';
                                    const match = text.match(/\\$\\s*[\\d\\.]+/);
                                    if (match) return match[0];
                                }
                            }
                            const all = document.body ? (document.body.innerText || '') : '';
                            const matches = all.match(/\\$\\s*[\\d]{1,3}(?:\\.\\d{3})+/g) || [];
                            return matches.length > 0 ? matches[matches.length - 1] : '';
                        }''')
                        await prod_page.close()
                        if extracted_price:
                            price_text = extracted_price
                    except Exception as e:
                        print(f"Fallback Cruz Verde para {href} error: {e}")

                m = re.search(r'\$\s*[\d\.]+', price_text) if price_text else None
                precio = m.group(0).replace(" ", "") if m else (price_text if price_text else "Consultar en tienda")

                resultados.append({
                    "nombre": name,
                    "precio": precio,
                    "url": href,
                    "disponible": bool(m),
                    "fuente": "Cruz Verde",
                })

            await browser.close()
    except Exception as e:
        print(f"Error en scraper Cruz Verde: {e}")

    return resultados
