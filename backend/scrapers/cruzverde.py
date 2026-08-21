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
                    const card = link.closest('div[class*="flex-col"], [class*="product"], [class*="card"]') || link.parentElement;
                    const text = (card ? card.innerText : link.innerText).trim();
                    const prices = text.match(/\\$\\s*[\\d\\.]+/g);
                    if (prices && prices.length > 0) {
                        const href = link.getAttribute('href') || '';
                        
                        let slugName = '';
                        const slugMatch = href.match(/\\/([a-zA-Z0-9\\-]+)\\/\\d+\\.html/);
                        if (slugMatch) {
                            slugName = slugMatch[1].replace(/--+/g, ' - ').replace(/-/g, ' ');
                            slugName = slugName.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
                        }

                        const lines = text.split('\\n').map(l => l.trim()).filter(Boolean);
                        const brand = lines.length > 0 && !lines[0].includes('$') && lines[0].length < 30 ? lines[0] : '';
                        
                        let finalName = slugName || (lines.find(l => !l.includes('$') && l.length > 3) || 'Medicamento');
                        if (brand && slugName && !slugName.toLowerCase().includes(brand.toLowerCase())) {
                            finalName = `${brand} - ${slugName}`;
                        }

                        const fullHref = href.startsWith('http') ? href : `https://www.cruzverde.cl${href.startsWith('/') ? '' : '/'}${href}`;
                        
                        if (!results.some(r => r.href === fullHref)) {
                            results.push({
                                name: finalName,
                                priceText: prices[prices.length - 1],
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
