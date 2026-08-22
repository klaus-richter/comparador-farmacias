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
                    // Solo seleccionar tarjetas de producto principales para evitar duplicados internos
                    const nodes = document.querySelectorAll('.product, .product-item, [class*="product-card"]');
                    for (const node of nodes) {
                        const linkEl = node.querySelector('a[href*="/products/"]');
                        if (!linkEl) continue;
                        const href = linkEl.getAttribute('href') || '';

                        const brandEl = node.querySelector('.product-name, [class*="brand"]');
                        const infoEl = node.querySelector('.product-info, [class*="product-info"], [class*="name"], h3, h2');
                        const brand = brandEl ? brandEl.innerText.trim() : '';
                        const info = infoEl ? infoEl.innerText.trim() : '';
                        let name = (brand && info && !info.toLowerCase().includes(brand.toLowerCase())) 
                            ? `${brand} - ${info}` 
                            : (info || brand || 'Medicamento');
                        // Asegurar nombre limpio
                        // Descartar productos agotados o sin existencias
                        const nodeText = node.innerText || '';
                        if (/agotado|sin\\s*stock|sin\\s*existencia|sin\\s*existencias|no\\s*disponible|out-of-stock/i.test(nodeText)) continue;

                        // Extracción estricta de "Precio Farmacia" / Envase completo
                        // 1. Descartar explícitamente elementos de precio unitario / fraccionado y precio tarjeta SbPay
                        const ignoreEls = node.querySelectorAll('.jss2, .jss7, [class*="unit-price"], [class*="price-per-unit"], [class*="unit_price"], .display-card-price, [class*="card-price"]');
                        ignoreEls.forEach(el => el.setAttribute('data-ignore-price', 'true'));

                        // 2. Prioridad 1: Buscar explícitamente "Precio Farmacia" / Precio Normal
                        const farmaciaSelectors = [
                            '.display-secoundary-price-normal',
                            '.display-secondary-price-normal',
                            '.display-normal-price',
                            '.display-price-normal',
                            '[class*="secoundary"]',
                            '[class*="secondary"]'
                        ];

                        let selectedPrice = null;
                        for (const sel of farmaciaSelectors) {
                            const el = node.querySelector(sel);
                            if (el && el.getAttribute('data-ignore-price') !== 'true') {
                                const text = (el.innerText || '').trim();
                                if (!/x\\s*1|\\/c[aá]p|\\/comp|\\/un|\\/dosis|unitario|fraccionad/i.test(text)) {
                                    const m = text.match(/\\$\\s*[\\d\\.]+/);
                                    if (m) {
                                        const num = parseInt(m[0].replace(/[^\\d]/g, ''), 10);
                                        if (num > 0) {
                                            selectedPrice = { str: m[0].replace(/\\s+/g, ''), num };
                                            break;
                                        }
                                    }
                                }
                            }
                        }

                        // 3. Prioridad 2: Si no tiene selector secundario, buscar precio oferta / general (sin tarjeta)
                        if (!selectedPrice) {
                            const fallbackSelectors = [
                                '.display-offer-price',
                                '.product-prices .price',
                                '.product-prices span:not([data-ignore-price="true"])'
                            ];
                            for (const sel of fallbackSelectors) {
                                const el = node.querySelector(sel);
                                if (el && el.getAttribute('data-ignore-price') !== 'true') {
                                    const text = (el.innerText || '').trim();
                                    if (!/x\\s*1|\\/c[aá]p|\\/comp|\\/un|\\/dosis|unitario|fraccionad/i.test(text)) {
                                        const m = text.match(/\\$\\s*[\\d\\.]+/);
                                        if (m) {
                                            const num = parseInt(m[0].replace(/[^\\d]/g, ''), 10);
                                            if (num > 0) {
                                                selectedPrice = { str: m[0].replace(/\\s+/g, ''), num };
                                                break;
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        // 4. Fallback por texto plano descartando precios de tarjeta o unitarios
                        if (!selectedPrice) {
                            const rawText = node.innerText || '';
                            const lines = rawText.split('\\n');
                            for (const line of lines) {
                                if (/x\\s*1|\\/c[aá]p|\\/comp|\\/un|\\/dosis|unitario|fraccionad|sbpay|tarjeta/i.test(line)) continue;
                                const m = line.match(/\\$\\s*[\\d\\.]+/);
                                if (m) {
                                    const num = parseInt(m[0].replace(/[^\\d]/g, ''), 10);
                                    if (num > 0) {
                                        selectedPrice = { str: m[0].replace(/\\s+/g, ''), num };
                                        break;
                                    }
                                }
                            }
                        }

                        if (name && selectedPrice) {
                            const fullHref = href.startsWith('http') ? href : `https://salcobrand.cl${href.startsWith('/') ? '' : '/'}${href}`;
                            if (!data.some(d => d.href === fullHref)) {
                                data.push({ name, priceText: selectedPrice.str, href: fullHref });
                            }
                        }
                    }
                    return data;
                }
            """)

            for item in items_data[:max_resultados]:
                resultados.append({
                    "nombre": item["name"],
                    "precio": item["priceText"],
                    "url": item["href"] or url,
                    "disponible": True,
                    "fuente": "Salcobrand",
                })

            await browser.close()
    except Exception as e:
        print(f"Error en scraper Salcobrand: {e}")

    return resultados
