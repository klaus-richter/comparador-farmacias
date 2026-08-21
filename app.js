// Configuración de API (soporta local y despliegue en la nube para GitHub Pages)
const API = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000"
  : "https://comparador-farmacias-backend.onrender.com"; // Cambiar por tu URL de Render o Railway

const statusBar = document.getElementById("status-bar");
const spinner = document.getElementById("spinner");
const statusTitle = document.getElementById("status-title");
const statusStep = document.getElementById("status-step");

const searchForm = document.getElementById("search-form");
const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const resultsWrapper = document.getElementById("results-wrapper");
const comparisonSummary = document.getElementById("comparison-summary");
const pharmacyGrid = document.getElementById("pharmacy-grid");

const ALL_PHARMACIES = [
  "Cruz Verde",
  "Salcobrand",
  "Farmacias Ahumada",
  "Dr. Simi",
  "Ecofarmacias"
];

// Mensajes variados, calmantes y descriptivos con emojis
const DYNAMIC_STEPS = [
  "🚀 Conectando de forma segura con las 5 farmacias más grandes de Chile...",
  "🔍 Consultando inventarios en Cruz Verde, Salcobrand, Ahumada, Dr. Simi y Ecofarmacias...",
  "💊 Conectando con los servidores de Farmacias Ahumada...",
  "🛒 Verificando promociones y ofertas vigentes en Salcobrand...",
  "⚡ Extrayendo disponibilidad inmediata en Cruz Verde...",
  "🧑‍⚕️ Buscando opciones genéricas y bioequivalentes en Dr. Simi...",
  "🌿 Consultando la base de datos de Ecofarmacias en tiempo real...",
  "📦 Verificando stock en farmacias online y centros de distribución...",
  "💰 Detectando descuentos automáticos y precios rebajados...",
  "🏷️ Identificando si hay convenios o formatos económicos por caja...",
  "🧪 Cotejando principios activos, dosis y presentaciones exactas...",
  "📋 Revisando miligramos, comprimidos, cápsulas, jarabes y gotas...",
  "🔎 Comparando marcas de laboratorio vs. genéricos económicos...",
  "📊 Calculando el costo por unidad de cada alternativa encontrada...",
  "⏳ Procesando todas las respuestas en paralelo...",
  "📈 Cruzando datos de precios entre las 5 cadenas farmacéuticas...",
  "🏪 Comprobando opciones de compra y retiro o despacho...",
  "💡 Evaluando cuál es el mix más conveniente para tu bolsillo...",
  "🎯 Seleccionando los mejores precios para cada medicamento...",
  "✨ Asignando la estrellita ⭐ al precio más bajo de cada fila...",
  "🧮 Sumando los totales por farmacia para la receta completa...",
  "🏆 Ordenando las columnas de la opción más barata a la más cara...",
  "🎨 Renderizando la tabla comparativa horizontal...",
  "🔗 Generando enlaces directos para comprar en cada farmacia...",
  "🚀 Casi listo! Consolidando todos los datos finales...",
  "🎉 Preparando la comparación definitiva para que ahorres al máximo..."
];

let progressInterval = null;
let currentPercent = 0;

function startWaitingAnimation(query) {
  statusBar.style.display = "flex";
  statusBar.className = "status-bar info";
  spinner.style.display = "block";
  currentPercent = 6;
  
  statusTitle.innerHTML = `Buscando medicamentos... <span class="progress-pct" id="progress-pct">6%</span>`;
  
  const fillEl = document.getElementById("progress-fill");
  if (fillEl) fillEl.style.width = "6%";

  let stepIndex = 0;
  statusStep.textContent = DYNAMIC_STEPS[0];
  statusStep.style.opacity = 1;

  if (progressInterval) clearInterval(progressInterval);

  progressInterval = setInterval(() => {
    // Incremento suave del porcentaje hasta el 95%
    if (currentPercent < 95) {
      currentPercent += Math.floor(Math.random() * 5) + 3;
      if (currentPercent > 95) currentPercent = 95;
    }
    const pctEl = document.getElementById("progress-pct");
    if (pctEl) pctEl.textContent = `${currentPercent}%`;

    const fillEl = document.getElementById("progress-fill");
    if (fillEl) fillEl.style.width = `${currentPercent}%`;

    // Cambiar mensaje a ritmo pausado y legible (~2.6 segundos)
    stepIndex = (stepIndex + 1) % DYNAMIC_STEPS.length;
    statusStep.style.opacity = 0;
    setTimeout(() => {
      statusStep.textContent = DYNAMIC_STEPS[stepIndex];
      statusStep.style.opacity = 1;
    }, 220);
  }, 2600);
}

function stopWaitingAnimation() {
  if (progressInterval) { 
    clearInterval(progressInterval); 
    progressInterval = null; 
  }
  const pctEl = document.getElementById("progress-pct");
  if (pctEl) pctEl.textContent = "100%";
  const fillEl = document.getElementById("progress-fill");
  if (fillEl) fillEl.style.width = "100%";
  spinner.style.display = "none";
  statusBar.style.display = "none";
}

function showErrorStatus(message) {
  stopWaitingAnimation();
  statusBar.style.display = "flex";
  statusBar.className = "status-bar error";
  statusTitle.textContent = "⚠️ Ocurrió un problema";
  statusStep.textContent = message;
}

function parsePriceToNumber(priceStr) {
  if (!priceStr || typeof priceStr !== "string") return Infinity;
  const digits = priceStr.replace(/[^\d]/g, "");
  if (!digits) return Infinity;
  const val = parseInt(digits, 10);
  return isNaN(val) || val <= 0 ? Infinity : val;
}

function getPharmacyLogo(fuente) {
  const f = (fuente || "").toLowerCase();
  let src = "";
  if (f.includes("ahumada"))    src = "https://www.farmaciasahumada.cl/favicon.ico";
  else if (f.includes("salco")) src = "https://salcobrand.cl/favicon.ico";
  else if (f.includes("cruz"))  src = "https://www.cruzverde.cl/favicon.ico";
  else if (f.includes("simi"))  src = "https://www.drsimi.cl/favicon.ico";
  else if (f.includes("eco"))   src = "https://www.ecofarmacias.cl/favicon.ico";
  if (!src) return "";
  return `<img src="${src}" class="pharmacy-logo" alt="${escapeHtml(fuente)}" onerror="this.style.display='none'">`;
}

function getPillClass(fuente) {
  const f = (fuente || "").toLowerCase();
  if (f.includes("ahumada")) return "pill-ahumada";
  if (f.includes("salco"))   return "pill-salcobrand";
  if (f.includes("cruz") || f.includes("verde")) return "pill-cruzverde";
  if (f.includes("simi"))    return "pill-drsimi";
  if (f.includes("eco"))     return "pill-ecofarmacias";
  return "pill-default";
}

function matchPharmacy(itemFuente, targetPharmacy) {
  const i = (itemFuente || "").toLowerCase();
  const t = (targetPharmacy || "").toLowerCase();
  if (t.includes("ahumada")) return i.includes("ahumada");
  if (t.includes("salco"))   return i.includes("salco");
  if (t.includes("cruz"))    return i.includes("cruz") || i.includes("verde");
  if (t.includes("simi"))    return i.includes("simi");
  if (t.includes("eco"))     return i.includes("eco");
  return false;
}

function renderRecipeComparison(receta, queryList) {
  pharmacyGrid.innerHTML = "";
  comparisonSummary.innerHTML = "";

  const pharmacies = ALL_PHARMACIES;

  // Pre-calcular la farmacia más barata POR MEDICAMENTO
  const cheapestPerMed = {};
  receta.forEach(r => {
    let minPrice = Infinity;
    let minPharmacy = null;
    pharmacies.forEach(fuente => {
      const items = (r.resultados || [])
        .filter(item => matchPharmacy(item.fuente, fuente))
        .sort((a, b) => parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio));
      const best = items[0];
      const p = best ? parsePriceToNumber(best.precio) : Infinity;
      if (p < minPrice) { minPrice = p; minPharmacy = fuente; }
    });
    cheapestPerMed[r.producto] = { pharmacy: minPharmacy, price: minPrice };
  });

  const totals = pharmacies.map(fuente => {
    let sum = 0;
    let availableCount = 0;
    const itemsByProd = [];

    receta.forEach(r => {
      const prodName = r.producto;
      const matchingItems = (r.resultados || [])
        .filter(item => matchPharmacy(item.fuente, fuente))
        .sort((a, b) => parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio));

      const bestItem = matchingItems[0] || null;
      const priceNum = bestItem ? parsePriceToNumber(bestItem.precio) : Infinity;

      if (priceNum !== Infinity) { sum += priceNum; availableCount++; }

      itemsByProd.push({ productoBuscado: prodName, bestItem, priceNum });
    });

    return { fuente, totalNum: availableCount === receta.length ? sum : Infinity, subtotalNum: sum, availableCount, totalCount: receta.length, itemsByProd };
  });

  totals.sort((a, b) => {
    if (a.totalNum !== Infinity && b.totalNum !== Infinity) return a.totalNum - b.totalNum;
    if (a.totalNum !== Infinity) return -1;
    if (b.totalNum !== Infinity) return 1;
    if (a.availableCount !== b.availableCount) return b.availableCount - a.availableCount;
    return a.subtotalNum - b.subtotalNum;
  });

  comparisonSummary.style.display = "none";

  totals.forEach((pharmacy, idx) => {
    const isWinner = idx === 0 && pharmacy.availableCount > 0 && pharmacy.totalNum !== Infinity;
    const pillClass = getPillClass(pharmacy.fuente);
    const logoHtml = getPharmacyLogo(pharmacy.fuente);

    const col = document.createElement("div");
    col.className = `pharmacy-column ${isWinner ? "winner" : ""}`;

    const priceDisplayText = pharmacy.totalNum !== Infinity
      ? `$${pharmacy.totalNum.toLocaleString("es-CL")}`
      : (pharmacy.availableCount > 0
          ? `$${pharmacy.subtotalNum.toLocaleString("es-CL")} (${pharmacy.availableCount}/${pharmacy.totalCount} items)`
          : "Incompleto");

    col.innerHTML = `
      <div class="col-header ${isWinner ? "winner-header" : ""}">
        <div class="pharmacy-badge-title ${pillClass}">
          ${logoHtml}
          ${pharmacy.fuente}
        </div>
        <span class="rank-badge ${isWinner ? "rank-winner" : "rank-other"}">
          ${isWinner ? "🏆 Receta Más Barata" : `#${idx + 1}`}
        </span>
      </div>

      <div class="col-best-offer">
        <span class="offer-label">Total de la receta completa:</span>
        <div class="offer-price-row">
          <span class="offer-price">${priceDisplayText}</span>
        </div>
      </div>

      <div class="col-recipe-items">
        <span class="alternatives-title">Desglose de medicamentos:</span>
        ${pharmacy.itemsByProd.map(item => {
          const isCheapestHere = cheapestPerMed[item.productoBuscado]
            && cheapestPerMed[item.productoBuscado].pharmacy
            && matchPharmacy(pharmacy.fuente, cheapestPerMed[item.productoBuscado].pharmacy)
            && item.priceNum !== Infinity;
          return `
          <div class="recipe-item-card ${isCheapestHere ? "cheapest-item" : ""}">
            <div class="recipe-item-head">
              <span class="recipe-prod-tag">${escapeHtml(item.productoBuscado)}</span>
              <span class="recipe-prod-price ${isCheapestHere ? "cheapest-price" : ""}">
                ${isCheapestHere ? "⭐ " : ""}${item.bestItem ? item.bestItem.precio : "Sin stock"}
              </span>
            </div>
            <div class="recipe-prod-name" title="${escapeHtml(item.bestItem ? item.bestItem.nombre : "No encontrado")}">${escapeHtml(item.bestItem ? item.bestItem.nombre : "No encontrado en esta farmacia")}</div>
            <div class="recipe-item-action">
              ${item.bestItem && item.bestItem.url ? `
                <a href="${item.bestItem.url}" target="_blank" rel="noopener noreferrer" class="alt-item action-link">
                  <span>Ver en tienda</span> <span>↗</span>
                </a>
              ` : `<span class="no-stock-label">Sin disponibilidad</span>`}
            </div>
          </div>
        `}).join("")}
      </div>
    `;

    pharmacyGrid.appendChild(col);
  });

  resultsWrapper.style.display = "flex";
}

function renderSingleComparison(products, query) {
  pharmacyGrid.innerHTML = "";
  comparisonSummary.innerHTML = "";

  if (!products || products.length === 0) {
    resultsWrapper.style.display = "none";
    showErrorStatus(`No encontramos resultados para "${query}".`);
    return;
  }

  const grouped = {};
  products.forEach(p => {
    const fuente = p.fuente || "Otra Farmacia";
    if (!grouped[fuente]) grouped[fuente] = [];
    grouped[fuente].push(p);
  });

  const pharmacyList = Object.keys(grouped).map(fuente => {
    const items = grouped[fuente].sort((a, b) => parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio));
    const bestItem = items[0] || null;
    const bestPriceNum = bestItem ? parsePriceToNumber(bestItem.precio) : Infinity;
    return { fuente, bestItem, bestPriceNum, alternatives: items.slice(1) };
  });

  pharmacyList.sort((a, b) => a.bestPriceNum - b.bestPriceNum);

  comparisonSummary.style.display = "none";

  pharmacyList.forEach((pharmacy, idx) => {
    const isWinner = idx === 0 && pharmacy.bestPriceNum !== Infinity;
    const pillClass = getPillClass(pharmacy.fuente);
    const logoHtml = getPharmacyLogo(pharmacy.fuente);

    const col = document.createElement("div");
    col.className = `pharmacy-column ${isWinner ? "winner" : ""}`;

    col.innerHTML = `
      <div class="col-header ${isWinner ? "winner-header" : ""}">
        <div class="pharmacy-badge-title ${pillClass}">
          ${logoHtml}
          ${pharmacy.fuente}
        </div>
        <span class="rank-badge ${isWinner ? "rank-winner" : "rank-other"}">
          ${isWinner ? "🏆 Más Barata" : `#${idx + 1}`}
        </span>
      </div>

      <div class="col-best-offer">
        <span class="offer-label">Mejor opción encontrada:</span>
        <div class="offer-price-row">
          <span class="offer-price">${pharmacy.bestItem ? pharmacy.bestItem.precio : "No disponible"}</span>
        </div>
        <div class="offer-name">${escapeHtml(pharmacy.bestItem ? pharmacy.bestItem.nombre : "Sin stock")}</div>
        ${pharmacy.bestItem && pharmacy.bestItem.url ? `
          <a href="${pharmacy.bestItem.url}" target="_blank" rel="noopener noreferrer" class="btn-buy-col">
            🛒 Comprar en ${pharmacy.fuente} ↗
          </a>
        ` : ""}
      </div>

      ${pharmacy.alternatives && pharmacy.alternatives.length > 0 ? `
        <div class="col-alternatives">
          <span class="alternatives-title">Otras opciones en ${pharmacy.fuente}:</span>
          ${pharmacy.alternatives.slice(0, 4).map(alt => `
            <a href="${alt.url}" target="_blank" rel="noopener noreferrer" class="alt-item" title="${escapeHtml(alt.nombre)}">
              <span class="alt-name">${escapeHtml(alt.nombre)}</span>
              <span class="alt-price">${alt.precio}</span>
            </a>
          `).join("")}
        </div>
      ` : ""}
    `;

    pharmacyGrid.appendChild(col);
  });

  resultsWrapper.style.display = "flex";
}

function escapeHtml(str) {
  return (str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

searchForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const rawQuery = searchInput.value.trim();
  if (!rawQuery) return;

  const queryItems = rawQuery.split(/[,;\n]+/).map(s => s.trim()).filter(Boolean);
  const isMultiple = queryItems.length > 1;

  resultsWrapper.style.display = "none";
  startWaitingAnimation(rawQuery);
  searchBtn.disabled = true;
  searchBtn.querySelector(".btn-text").textContent = "Comparando...";

  try {
    if (isMultiple) {
      const res = await fetch(`${API}/api/buscar-receta?q=${encodeURIComponent(queryItems.join(","))}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const data = await res.json();
      if (data.status === "ok") { stopWaitingAnimation(); renderRecipeComparison(data.receta, queryItems); }
    } else {
      const res = await fetch(`${API}/api/buscar?q=${encodeURIComponent(rawQuery)}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      const data = await res.json();
      if (data.status === "ok") { stopWaitingAnimation(); renderSingleComparison(data.resultados, rawQuery); }
    }
  } catch (err) {
    showErrorStatus(`Error conectando con el backend: ${err.message}`);
  } finally {
    searchBtn.disabled = false;
    searchBtn.querySelector(".btn-text").textContent = "Comparar precios";
  }
});
