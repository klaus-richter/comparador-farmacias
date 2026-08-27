// Configuración de API (soporta local y despliegue en Google Cloud Run para GitHub Pages)
const API = "https://comparador-backend-201153254876.us-central1.run.app";


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

// Hitos de búsqueda estructurados y perfectamente sincronizados con el porcentaje
const SEARCH_MILESTONES = [
  { minPct: 0,  maxPct: 24, text: "🚀 Conectando y consultando las 5 farmacias de Chile..." },
  { minPct: 25, maxPct: 54, text: "🔍 Extrayendo precios y stock en tiempo real..." },
  { minPct: 55, maxPct: 79, text: "✨ Comparando alternativas y buscando las opciones más baratas..." },
  { minPct: 80, maxPct: 94, text: "🧮 Calculando el total más económico para tu receta completa..." },
  { minPct: 95, maxPct: 100, text: "🏆 ¡Listo! Consolidando la mejor comparación para tu bolsillo..." }
];

let progressInterval = null;
let currentPercent = 0;
let currentMilestoneIndex = -1;

function updateMilestoneText(pct) {
  const milestone = SEARCH_MILESTONES.find(m => pct >= m.minPct && pct <= m.maxPct);
  if (milestone && statusStep.textContent !== milestone.text) {
    statusStep.style.transition = "opacity 0.20s ease, transform 0.20s ease";
    statusStep.style.opacity = "0";
    statusStep.style.transform = "translateY(2px)";
    setTimeout(() => {
      statusStep.textContent = milestone.text;
      statusStep.style.opacity = "1";
      statusStep.style.transform = "none";
    }, 180);
  }
}

function startWaitingAnimation(query) {
  statusBar.style.display = "flex";
  statusBar.className = "status-bar info";
  currentPercent = 0;
  currentMilestoneIndex = 0;
  
  statusTitle.innerHTML = `Buscando medicamentos... <span class="progress-pct" id="progress-pct">0%</span>`;
  statusStep.textContent = SEARCH_MILESTONES[0].text;
  statusStep.style.opacity = "1";
  
  const fillEl = document.getElementById("progress-fill");
  if (fillEl) fillEl.style.width = "0%";

  if (progressInterval) {
    clearTimeout(progressInterval);
    clearInterval(progressInterval);
  }

  // Avance coherente de 1 en 1 sincronizado con los hitos reales
  function tickProgress() {
    if (currentPercent >= 98) return;
    currentPercent += 1;

    const pctEl = document.getElementById("progress-pct");
    if (pctEl) pctEl.textContent = `${currentPercent}%`;

    const fillEl = document.getElementById("progress-fill");
    if (fillEl) fillEl.style.width = `${currentPercent}%`;

    // Sincronizar el mensaje del hito correspondiente
    updateMilestoneText(currentPercent);

    // Ritmo natural y cómodo (total ~7 a 8 segundos)
    let delay = 60; // 0% a 25%: conexión (~1.5s)
    if (currentPercent >= 25 && currentPercent < 55) {
      delay = 75; // 25% a 55%: extracción de datos (~2.2s)
    } else if (currentPercent >= 55 && currentPercent < 80) {
      delay = 95; // 55% a 80%: comparación de precios (~2.3s)
    } else if (currentPercent >= 80 && currentPercent < 95) {
      delay = 140; // 80% a 95%: cálculo de totales (~2.1s)
    } else if (currentPercent >= 95) {
      delay = 300; // 95% a 98%: espera final
    }

    progressInterval = setTimeout(tickProgress, delay);
  }

  progressInterval = setTimeout(tickProgress, 40);
}

function stopWaitingAnimation() {
  if (progressInterval) { 
    clearTimeout(progressInterval); 
    clearInterval(progressInterval);
    progressInterval = null; 
  }
  const pctEl = document.getElementById("progress-pct");
  if (pctEl) pctEl.textContent = "100%";
  const fillEl = document.getElementById("progress-fill");
  if (fillEl) fillEl.style.width = "100%";
  updateMilestoneText(100);
  
  setTimeout(() => {
    statusBar.style.display = "none";
  }, 180);
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
  // 1. Usar motor semántico del ISP si está disponible en ventana
  if (typeof window !== "undefined" && window.ISPEngine) {
    const isMatch = window.ISPEngine.matchProductAgainstQuery(prodName, searchQuery);
    if (isMatch) return true;
  }

  // 2. Fallback heurístico léxico
  const normProd = normalizeSearchText(prodName);
  const normQuery = normalizeSearchText(searchQuery);

  const qTokens = normQuery.split(/\s+/).filter(tok => tok.length >= 2);
  if (qTokens.length === 0) return true;

  const keywords = qTokens.filter(tok => !/^\d+$/.test(tok) && !['comp', 'comprimidos', 'capsulas', 'mg', 'mcg', 'x'].includes(tok));

  if (keywords.length > 0) {
    const mainWord = keywords[0];
    if (!normProd.includes(mainWord)) {
      return false;
    }
  }

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

  // TIER 1: Coincidencia directa con la palabra clave o marca buscada
  const exactMatches = items.filter(item => matchProductInteligente(item.nombre, searchProd));
  if (exactMatches.length > 0) {
    exactMatches.sort((a, b) => parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio));
    return exactMatches[0];
  }

  // TIER 2: Fallback Inteligente cuando se busca por Principio Activo (ej: rupatadina en Ahumada que solo titula como Rupax/Rexanel)
  const normQuery = normalizeSearchText(searchProd);
  const queryNums = normQuery.split(/\s+/).filter(tok => /^\d+$/.test(tok));
  
  let fallbackCandidates = items;
  if (queryNums.length > 0) {
    const doseMatches = items.filter(item => {
      const prodNums = normalizeSearchText(item.nombre).match(/\b\d+\b/g) || [];
      return queryNums.some(num => prodNums.includes(num));
    });
    if (doseMatches.length > 0) {
      fallbackCandidates = doseMatches;
    }
  }

  fallbackCandidates.sort((a, b) => parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio));
  return fallbackCandidates[0];
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

    // Si NINGUNA farmacia tiene ningún medicamento (búsqueda inexistente o mal escrita)
  if (available.length === 0) {
    pharmacyGrid.innerHTML = `
      <div class="empty-search-alert">
        <span class="empty-alert-icon">⚠️</span>
        <span class="empty-alert-text">No encontramos resultados. Verifica que el nombre esté bien escrito.</span>
      </div>
    `;
    comparisonSummary.style.display = "none";
    resultsWrapper.style.display = "flex";
    return;
  }

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
  resultsWrapper.classList.remove("visible");
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
      // 1. Llevar barra al 100% de inmediato
      const pctEl = document.getElementById("progress-pct");
      if (pctEl) pctEl.textContent = "100%";
      const fillEl = document.getElementById("progress-fill");
      if (fillEl) fillEl.style.width = "100%";

      // 2. Transición suave de salida de la barra (fade out)
      statusBar.style.opacity = "0";
      statusBar.style.transform = "translateY(-4px)";

      setTimeout(() => {
        stopWaitingAnimation();
        statusBar.style.opacity = "1";
        statusBar.style.transform = "none";

        // 3. Renderizar resultados con fade in fluido
        renderRecipeComparison(data.receta, queryItems);
        resultsWrapper.style.display = "flex";
        requestAnimationFrame(() => {
          resultsWrapper.classList.add("visible");
        });
      }, 160);
    }
  } catch (err) {
    showErrorStatus(`Error conectando con el backend: ${err.message}`);
  } finally {
    searchBtn.disabled = false;
    searchBtn.querySelector(".btn-text").textContent = "Buscar Precios";
  }
});





// Contador discreto de visitas

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initVisitorCounter);
} else {
  
}

// Telemetría Silenciosa (Búsquedas y Clics)
function trackSearchEvent(receta, queryList, elapsedSecs) {
  try {
    const winnerCard = document.querySelector('.pharmacy-card.winner h2, .winner .pharmacy-header h2');
    const winnerPharmacy = winnerCard ? winnerCard.innerText.replace(/[^a-zA-Z\s\.]/g, '').trim() : null;
    const winnerTotalEl = document.querySelector('.winner .total-amount, .winner .pharmacy-total');
    const winnerPrice = winnerTotalEl ? winnerTotalEl.innerText.trim() : null;

    fetch(`${API_BASE_URL}/api/analytics/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: queryList.join(", "),
        med_count: queryList.length,
        elapsed_ms: Math.round((elapsedSecs || 0) * 1000),
        is_cache: elapsedSecs < 1.5,
        winner_pharmacy: winnerPharmacy,
        winner_price: winnerPrice,
        user_agent: navigator.userAgent
      })
    }).catch(() => {});
  } catch (e) {}
}

function trackClickEvent(medicineName, pharmacyName, price, url, isCheapest) {
  try {
    fetch(`${API_BASE_URL}/api/analytics/click`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        medicine: medicineName,
        pharmacy: pharmacyName,
        price: price,
        url: url,
        is_cheapest: !!isCheapest
      })
    }).catch(() => {});
  } catch (e) {}
}

// Click en Logo para reiniciar/refrescar la página a Home
document.addEventListener("DOMContentLoaded", () => {
  const logo = document.querySelector(".app-top-nav");
  if (logo) {
    logo.style.cursor = "pointer";
    logo.addEventListener("click", () => {
      window.location.href = "/";
    });
  }
});

// Hipervínculo táctil y de clic infalible en Logo QueFarmacia.cl
document.addEventListener("DOMContentLoaded", () => {
  const logoElements = document.querySelectorAll(".logo-home-link, .app-top-nav, .logo-breaking-bad-wrapper");
  logoElements.forEach(el => {
    el.style.cursor = "pointer";
    el.addEventListener("click", (e) => {
      e.preventDefault();
      window.location.href = "https://quefarmacia.cl/";
    });
  });
});
