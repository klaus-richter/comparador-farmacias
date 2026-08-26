// Configuración de API (soporta local y despliegue en Google Cloud Run para GitHub Pages)
const API = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
  ? "http://localhost:8000"
  : "https://comparador-backend-201153254876.us-central1.run.app";


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
  // Omitido para mantener consistencia visual uniforme entre todas las farmacias
  return "";
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

function normalizeSearchText(text) {
  if (!text) return "";
  let t = text.toLowerCase();
  // Separar números de unidades: 100mcg -> 100 mcg, 500mg -> 500 mg, 100comprimidos -> 100 comprimidos
  t = t.replace(/(\d+)\s*(mg|mcg|g|ml|comp|comprimidos|capsulas|sobres)/gi, '$1 $2');
  // Normalizar acentos
  t = t.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  // Normalizar fonética para i/y, b/v, z/s
  t = t.replace(/y/g, 'i').replace(/v/g, 'b').replace(/z/g, 's');
  // Limpiar signos
  t = t.replace(/[^\w\s]/g, ' ');
  return t.replace(/\s+/g, ' ').trim();
}

function matchProductInteligente(prodName, searchQuery) {
  const normProd = normalizeSearchText(prodName);
  const normQuery = normalizeSearchText(searchQuery);

  const qTokens = normQuery.split(/\s+/).filter(tok => tok.length >= 2);
  if (qTokens.length === 0) return true;

  // Palabras no numéricas clave (ej: 'eutirox', 'acido', 'acetilsalicilico', 'avamis')
  const keywords = qTokens.filter(tok => !/^\d+$/.test(tok) && !['comp', 'comprimidos', 'capsulas', 'mg', 'mcg', 'x'].includes(tok));

  // Al menos la primera palabra principal DEBE estar en el producto
  if (keywords.length > 0) {
    const mainWord = keywords[0];
    if (!normProd.includes(mainWord)) {
      return false;
    }
  }

  // Si el usuario especificó dosis numérica (ej: '100', '500', '25', '850'), debe coincidir
  const queryNums = qTokens.filter(tok => /^\d+$/.test(tok));
  if (queryNums.length > 0) {
    const prodNums = normProd.match(/\b\d+\b/g) || [];
    if (!queryNums.some(num => prodNums.includes(num))) {
      return false;
    }
  }

  return true;
}

// Función con cascadeo inteligente: respeta marcas exactas y evita sustitutos no solicitados
function getBestItemForPharmacy(allResults, targetPharmacy, searchProd) {
  // 1. Filtrar productos de esta farmacia con precio válido
  const items = (allResults || [])
    .filter(item => matchPharmacy(item.fuente, targetPharmacy))
    .filter(item => parsePriceToNumber(item.precio) !== Infinity);

  if (items.length === 0) return null;

  // 2. Filtrar por match inteligente (marca, dosis y fonética)
  const matches = items.filter(item => matchProductInteligente(item.nombre, searchProd));

  if (matches.length > 0) {
    matches.sort((a, b) => parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio));
    return matches[0];
  }

  return null;
}


function renderRecipeComparison(receta, queryList) {
  pharmacyGrid.innerHTML = "";
  comparisonSummary.innerHTML = "";

  const pharmacies = ALL_PHARMACIES;

  // Pre-calcular la farmacia más barata POR MEDICAMENTO con cascadeo
  const cheapestPerMed = {};
  receta.forEach(r => {
    let minPrice = Infinity;
    let minPharmacy = null;
    pharmacies.forEach(fuente => {
      const best = getBestItemForPharmacy(r.resultados, fuente, r.producto);
      const p = best ? parsePriceToNumber(best.precio) : Infinity;
      if (p < minPrice) { minPrice = p; minPharmacy = fuente; }
    });
    cheapestPerMed[r.producto] = { pharmacy: minPharmacy, price: minPrice };
  });

  let totals = pharmacies.map(fuente => {
    let sum = 0;

    let availableCount = 0;
    let starCount = 0;
    const itemsByProd = [];

    receta.forEach(r => {
      const prodName = r.producto;
      const bestItem = getBestItemForPharmacy(r.resultados, fuente, prodName);
      const priceNum = bestItem ? parsePriceToNumber(bestItem.precio) : Infinity;

      if (priceNum !== Infinity) { 
        sum += priceNum; 
        availableCount++; 
      }

      const isCheapestHere = cheapestPerMed[prodName]
        && cheapestPerMed[prodName].pharmacy
        && matchPharmacy(fuente, cheapestPerMed[prodName].pharmacy)
        && priceNum !== Infinity;

      if (isCheapestHere) {
        starCount++;
      }

      itemsByProd.push({ productoBuscado: prodName, bestItem, priceNum, isCheapestHere });
    });

    const isComplete = availableCount === receta.length;
    return { 

      fuente, 
      isComplete, 
      totalNum: isComplete ? sum : Infinity, 
      subtotalNum: sum, 
      availableCount, 
      totalCount: receta.length, 
      starCount, 
      itemsByProd 
    };
  });

  // Lógica de ordenamiento solicitada:
  // 1. Ganador (#1): La farmacia que tenga la receta completa y sea la de MENOR COSTO TOTAL ($).
  // 2. Lugares #2, #3, #4, #5: Ordenados por mayor cantidad de estrellitas ⭐ (mejores precios unitarios),
  //    desempatando por menor subtotal/total.
  // 3. Farmacias con 0 disponibilidad al final.
  
  // Separar farmacias con disponibilidad de las que tienen 0
  const available = totals.filter(t => t.availableCount > 0);
  const unavailable = totals.filter(t => t.availableCount === 0);

  // Buscar si hay farmacias completas
  const completePharmacies = available.filter(t => t.isComplete);
  let winner = null;
  let remaining = [];

  if (completePharmacies.length > 0) {
    // La ganadora #1 es la completa con menor precio total
    completePharmacies.sort((a, b) => a.totalNum - b.totalNum);
    winner = completePharmacies[0];
    remaining = available.filter(t => t.fuente !== winner.fuente);
  } else {
    // Si ninguna está completa, la primera por estrellas es la ganadora
    remaining = [...available];
  }

  // Ordenar el resto de farmacias por:
  // 1. Mayor cantidad de Estrellas ⭐ (mejores precios unitarios)
  // 2. A igual cantidad de estrellas: Mayor cantidad de medicamentos disponibles (ej: 4/5 le gana a 3/5)
  // 3. A igual cantidad de medicamentos: Menor precio total / subtotal ($)
  remaining.sort((a, b) => {
    if (a.starCount !== b.starCount) {
      return b.starCount - a.starCount;
    }
    if (a.availableCount !== b.availableCount) {
      return b.availableCount - a.availableCount;
    }
    const priceA = a.totalNum !== Infinity ? a.totalNum : a.subtotalNum;
    const priceB = b.totalNum !== Infinity ? b.totalNum : b.subtotalNum;
    return priceA - priceB;
  });

  if (winner) {
    totals = [winner, ...remaining, ...unavailable];
  } else {
    totals = [...remaining, ...unavailable];
  }




  comparisonSummary.style.display = "none";

  totals.forEach((pharmacy, idx) => {
    const isWinner = idx === 0 && pharmacy.availableCount > 0;
    const pillClass = getPillClass(pharmacy.fuente);
    const logoHtml = getPharmacyLogo(pharmacy.fuente);

    const col = document.createElement("div");
    col.className = `pharmacy-column ${isWinner ? "winner" : ""}`;

    const priceDisplayText = pharmacy.totalNum !== Infinity
      ? `$${pharmacy.totalNum.toLocaleString("es-CL")}`
      : (pharmacy.availableCount > 0
          ? `$${pharmacy.subtotalNum.toLocaleString("es-CL")}`
          : "-");

    col.innerHTML = `
      <div class="col-header ${isWinner ? "winner-header" : ""}">
        <div class="pharmacy-badge-title ${pillClass}">
          ${logoHtml}
          ${pharmacy.fuente}
        </div>
        <span class="rank-badge ${isWinner ? "rank-winner" : "rank-other"}">
          ${isWinner ? "🏆 Más Económica" : `#${idx + 1}`}
        </span>
      </div>

      <div class="col-best-offer">
        <span class="offer-label">Total de la receta completa:</span>
        <div class="offer-price-row">
          <span class="offer-price">${priceDisplayText}</span>
        </div>
      </div>

      <div class="col-recipe-items">
        ${pharmacy.itemsByProd.map(item => `
          <div class="recipe-item-card ${item.isCheapestHere ? "cheapest-item" : ""}">
            <div class="recipe-item-head">
              <span class="recipe-prod-tag">${escapeHtml(item.productoBuscado)}</span>
              <div class="recipe-item-right">
                <span class="recipe-prod-price ${item.isCheapestHere ? "cheapest-price" : ""} ${!item.bestItem ? "price-no-stock" : ""}">
                  ${item.isCheapestHere ? '<span class="star-badge">⭐</span>' : ""}${item.bestItem ? item.bestItem.precio : "Sin stock"}
                </span>
                ${item.bestItem && item.bestItem.url ? `
                  <a href="${item.bestItem.url}" target="_blank" rel="noopener noreferrer" class="icon-link-btn" title="Ver producto en la farmacia">
                    ↗
                  </a>
                ` : `<span class="icon-placeholder"></span>`}
              </div>
            </div>
          </div>
        `).join("")}
      </div>
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

  let queryItems = rawQuery.split(/[,;\n]+/).map(s => s.trim()).filter(Boolean);

  // Validación de texto no válido o copia de instrucciones
  const normalizedQuery = rawQuery.toLowerCase();
  const invalidPhrases = [
    "ingresa los medicamentos",
    "separados por coma",
    "compara precios",
    "maximo 5 medicamentos",
    "comparador de farmacias",
    "ej:"
  ];
  const isInstructional = invalidPhrases.some(phrase => normalizedQuery.includes(phrase));
  const isSentence = queryItems.length === 1 && queryItems[0].split(/\s+/).length >= 4 && !/\d+\s*(mg|g|ml|mcg|comprimidos|capsulas)/i.test(queryItems[0]);

  if (isInstructional || isSentence) {
    showErrorStatus("⚠️ Por favor ingresa nombres de medicamentos válidos separados por coma (ej: paracetamol, omeprazol).");
    setTimeout(() => { statusBar.style.display = "none"; }, 4000);
    return;
  }

  // Limitar a 10 medicamentos máximo
  if (queryItems.length > 10) {
    queryItems = queryItems.slice(0, 10);
    searchInput.value = queryItems.join(", ");
    showErrorStatus("⚠️ Máximo 10 medicamentos por búsqueda. Se tomaron los primeros 10.");
    setTimeout(() => { statusBar.style.display = "none"; }, 3500);
  }


  const isMultiple = queryItems.length > 1;

  resultsWrapper.style.display = "none";
  startWaitingAnimation(rawQuery);
  searchBtn.disabled = true;
  searchBtn.querySelector(".btn-text").textContent = "Comparando...";

  const minWaitPromise = new Promise(resolve => setTimeout(resolve, 2000));

  try {
    const fetchPromise = fetch(`${API}/api/buscar-receta?q=${encodeURIComponent(queryItems.join(","))}`)
      .then(async res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return await res.json();
      });
    const [data] = await Promise.all([fetchPromise, minWaitPromise]);
    if (data.status === "ok") { 
      stopWaitingAnimation(); 
      renderRecipeComparison(data.receta, queryItems); 
    }
  } catch (err) {
    showErrorStatus(`Error conectando con el backend: ${err.message}`);
  } finally {
    searchBtn.disabled = false;
    searchBtn.querySelector(".btn-text").textContent = "Buscar Precios";
  }
});

