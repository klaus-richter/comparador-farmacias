import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.cruzverde.cl"

async def buscar_cruzverde(producto: str, max_resultados: int = 6) -> list[dict]:
    """
    Busca un producto en Farmacias Cruz Verde usando la URL directa.
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
                await page.wait_for_timeout(3000)

            items_data = await page.evaluate('''() => {
                const results = [];
                const links = Array.from(document.querySelectorAll('a[href*=".html"]'));
                for (const link of links) {
                    const href = link.getAttribute('href') || '';
                    if (!href || !href.endsWith('.html')) continue;

                    let curr = link;
                    let text = '';
                    for (let i = 0; i < 6; i++) {
                        if (curr) {
                            text = curr.innerText || '';
                            if (text.includes('$')) break;
                            curr = curr.parentElement;
                        }
                    }

                    const prices = (text || '').match(/\\$\\s*[\\d\\.]+/g);
                    if (prices && prices.length > 0) {
                        const linkText = link.innerText.trim();
                        let name = linkText;

                        // Si el link actual no tiene texto (ej: link sobre imagen), buscar en el bloque
                        if (!name) {
                            const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                            name = lines.find(l => !l.includes('$') && !l.includes('%') && l.length > 3) || '';
                        }

                        // Fallback por slug si el texto falló
                        if (!name) {
                            const slugMatch = href.match(/\\/([a-zA-Z0-9\\-]+)\\/\\d+\\.html/);
                            if (slugMatch) {
                                name = slugMatch[1]
                                    .replace(/-/g, ' ')
                                    .split(' ')
                                    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
                                    .join(' ');
                            }
                        }

                        const fullHref = href.startsWith('http') ? href : `https://www.cruzverde.cl${href.startsWith('/') ? '' : '/'}${href}`;
                        
                        // Usar el precio con descuento si existe (último precio listado)
                        const bestPrice = prices[prices.length - 1];

                        if (name && !results.some(r => r.href === fullHref)) {
                            results.push({
                                name: name,
                                priceText: bestPrice,
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
                    "url": item["href"],
                    "disponible": bool(m),
                    "fuente": "Cruz Verde",
                })

            await browser.close()
    except Exception as e:
        print(f"Error en scraper Cruz Verde: {e}")

    return resultados
