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

const DYNAMIC_STEPS = [
  "Revisando catálogo y ofertas disponibles...",
  "Cotizando en Cruz Verde, Salcobrand y Ahumada...",
  "Consultando opciones en Dr. Simi y Ecofarmacias...",
  "Identificando mejores precios y bioequivalentes...",
  "Optimizando el total de tu receta completa..."
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
    if (currentPercent < 95) {
      currentPercent += Math.floor(Math.random() * 5) + 3;
      if (currentPercent > 95) currentPercent = 95;
    }
    const pctEl = document.getElementById("progress-pct");
    if (pctEl) pctEl.textContent = `${currentPercent}%`;

    const fillEl = document.getElementById("progress-fill");
    if (fillEl) fillEl.style.width = `${currentPercent}%`;

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
  
  setTimeout(() => {
    statusBar.style.display = "none";
    searchBtn.disabled = false;
  }, 400);
}

function showErrorStatus(message) {
  if (progressInterval) clearInterval(progressInterval);
  statusBar.style.display = "flex";
  statusBar.className = "status-bar error";
  spinner.style.display = "none";
  statusTitle.textContent = "Atención";
  statusStep.textContent = message;
  statusStep.style.opacity = 1;
  searchBtn.disabled = false;
}

function parsePriceToNumber(priceStr) {
  if (!priceStr) return Infinity;
  const digits = String(priceStr).replace(/[^\d]/g, "");
  return digits ? parseInt(digits, 10) : Infinity;
}

function getPillClass(pharmacyName) {
  const name = pharmacyName.toLowerCase();
  if (name.includes("cruz"))    return "pill-cruz-verde";
  if (name.includes("salco"))   return "pill-salcobrand";
  if (name.includes("ahumada")) return "pill-ahumada";
  if (name.includes("simi"))    return "pill-dr-simi";
  if (name.includes("eco"))     return "pill-ecofarmacias";
  return "";
}

function getPharmacyLogo(pharmacyName) {
  const name = pharmacyName.toLowerCase();
  if (name.includes("cruz"))    return `<span class="pharmacy-icon-dot dot-cv"></span>`;
  if (name.includes("salco"))   return `<span class="pharmacy-icon-dot dot-sb"></span>`;
  if (name.includes("ahumada")) return `<span class="pharmacy-icon-dot dot-fa"></span>`;
  if (name.includes("simi"))    return `<span class="pharmacy-icon-dot dot-ds"></span>`;
  if (name.includes("eco"))     return `<span class="pharmacy-icon-dot dot-eco"></span>`;
  return "";
}

function matchPharmacy(itemFuente, targetPharmacy) {
  const i = (itemFuente || "").toLowerCase();
  const t = (targetPharmacy || "").toLowerCase();
  if (t.includes("cruz"))    return i.includes("cruz");
  if (t.includes("salco"))   return i.includes("salco");
  if (t.includes("ahumada")) return i.includes("ahumada");
  if (t.includes("simi"))    return i.includes("simi");
  if (t.includes("eco"))     return i.includes("eco");
  return false;
}

function normalizeSearchText(text) {
  if (!text) return "";
  let t = text.toLowerCase();
  t = t.replace(/(\d+)\s*(mg|mcg|g|ml|comp|comprimidos|capsulas|sobres)/gi, '$1 $2');
  t = t.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  t = t.replace(/y/g, 'i').replace(/v/g, 'b').replace(/z/g, 's');
  t = t.replace(/[^\w\s]/g, ' ');
  return t.replace(/\s+/g, ' ').trim();
}

function matchProductInteligente(prodName, searchQuery) {
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

function getBestItemForPharmacy(allResults, targetPharmacy, searchProd) {
  const items = (allResults || [])
    .filter(item => matchPharmacy(item.fuente, targetPharmacy))
    .filter(item => parsePriceToNumber(item.precio) !== Infinity);

  if (items.length === 0) return null;

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

  // 1. Pre-calcular la farmacia más barata POR MEDICAMENTO (para la estrellita ⭐)
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

  // 2. Calcular totales por farmacia
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

  // 3. Ordenamiento: Ganador #1 (Receta completa + menor precio) -> estrellas -> disponibilidad -> subtotal
  const available = totals.filter(t => t.availableCount > 0);
  const unavailable = totals.filter(t => t.availableCount === 0);
  const completePharmacies = available.filter(t => t.isComplete);
  let winner = null;
  let remaining = [];

  if (completePharmacies.length > 0) {
    completePharmacies.sort((a, b) => a.totalNum - b.totalNum);
    winner = completePharmacies[0];
    remaining = available.filter(t => t.fuente !== winner.fuente);
  } else {
    remaining = [...available];
  }

  remaining.sort((a, b) => {
    if (a.starCount !== b.starCount) return b.starCount - a.starCount;
    if (a.availableCount !== b.availableCount) return b.availableCount - a.availableCount;
    const priceA = a.totalNum !== Infinity ? a.totalNum : a.subtotalNum;
    const priceB = b.totalNum !== Infinity ? b.totalNum : b.subtotalNum;
    return priceA - priceB;
  });

  if (winner) {
    totals = [winner, ...remaining, ...unavailable];
  } else {
    totals = [...remaining, ...unavailable];
  }

  // 4. Banner de Ganador #1
  if (winner && winner.availableCount > 0) {
    const winnerLogo = getPharmacyLogo(winner.fuente);
    const winnerPill = getPillClass(winner.fuente);
    comparisonSummary.innerHTML = `
      <div class="winner-summary-card">
        <div class="winner-summary-left">
          <span class="winner-trophy">🏆</span>
          <div>
            <div class="winner-tag">FARMACIA MÁS ECONÓMICA</div>
            <div class="winner-name-row">
              <span class="pharmacy-badge-title ${winnerPill}">${winnerLogo} ${winner.fuente}</span>
              <span class="winner-badge-pill">${winner.availableCount}/${receta.length} disponibles</span>
            </div>
          </div>
        </div>
        <div class="winner-summary-right">
          <span class="winner-price-label">Total de la receta:</span>
          <span class="winner-total-price">$${winner.totalNum.toLocaleString("es-CL")}</span>
        </div>
      </div>
    `;
    comparisonSummary.style.display = "block";
  } else {
    comparisonSummary.style.display = "none";
  }

  // 5. Generar Matriz Compacta Optimizada para Móvil
  const matrixWrapper = document.createElement("div");
  matrixWrapper.className = "matrix-wrapper";

  let tableHtml = `
    <table class="matrix-table">
      <thead>
        <tr>
          <th class="col-fixed-med">
            <span class="th-label-med">📋 Medicamento</span>
          </th>
          ${totals.map((pharm, idx) => {
            const isWin = idx === 0 && pharm.availableCount > 0;
            const logo = getPharmacyLogo(pharm.fuente);
            const pill = getPillClass(pharm.fuente);
            const priceText = pharm.totalNum !== Infinity 
              ? `$${pharm.totalNum.toLocaleString("es-CL")}` 
              : (pharm.availableCount > 0 ? `$${pharm.subtotalNum.toLocaleString("es-CL")}` : "-");
            return `
              <th class="col-pharm ${isWin ? 'th-winner' : ''}">
                <div class="th-pharm-top">
                  <span class="rank-badge ${isWin ? 'rank-winner' : 'rank-other'}">${isWin ? '🏆 #1' : '#' + (idx + 1)}</span>
                  <div class="pharm-title-badge ${pill}">${logo} ${pharm.fuente}</div>
                </div>
                <div class="th-pharm-total">
                  <span class="th-total-amount">${priceText}</span>
                  <span class="th-total-disp">${pharm.availableCount}/${receta.length} disp</span>
                </div>
              </th>
            `;
          }).join('')}
        </tr>
      </thead>
      <tbody>
  `;

  // Filas por cada medicamento de la receta
  receta.forEach((r, medIdx) => {
    const prodName = r.producto;
    tableHtml += `
      <tr>
        <td class="col-fixed-med med-row-cell">
          <div class="med-info-box">
            <span class="med-idx">#${medIdx + 1}</span>
            <span class="med-name-primary">${escapeHtml(prodName)}</span>
          </div>
        </td>
    `;

    totals.forEach(pharm => {
      const matchData = pharm.itemsByProd.find(it => it.productoBuscado === prodName);
      const bestItem = matchData ? matchData.bestItem : null;
      const isStar = matchData ? matchData.isCheapestHere : false;

      if (bestItem && matchData.priceNum !== Infinity) {
        tableHtml += `
          <td class="col-pharm price-cell ${isStar ? 'star-winner-cell' : ''}">
            <div class="price-cell-box">
              <div class="price-top-line">
                ${isStar ? '<span class="star-badge" title="Mejor precio">⭐</span>' : ''}
                <span class="item-price">${escapeHtml(bestItem.precio)}</span>
                <a href="${bestItem.url}" target="_blank" rel="noopener noreferrer" class="link-arrow" title="Ver en ${pharm.fuente}">↗</a>
              </div>
              <span class="item-full-name" title="${escapeHtml(bestItem.nombre)}">${escapeHtml(bestItem.nombre)}</span>
            </div>
          </td>
        `;
      } else {
        tableHtml += `
          <td class="col-pharm price-cell cell-empty">
            <span class="empty-stock">Sin stock</span>
          </td>
        `;
      }
    });

    tableHtml += `</tr>`;
  });

  // Fila de Totales al final
  tableHtml += `
      </tbody>
      <tfoot>
        <tr class="tfoot-row">
          <td class="col-fixed-med tfoot-label">
            <strong>TOTAL RECETA</strong>
          </td>
          ${totals.map((pharm, idx) => {
            const isWin = idx === 0 && pharm.availableCount > 0;
            const priceText = pharm.totalNum !== Infinity 
              ? `$${pharm.totalNum.toLocaleString("es-CL")}` 
              : (pharm.availableCount > 0 ? `$${pharm.subtotalNum.toLocaleString("es-CL")}` : "-");
            return `
              <td class="col-pharm tfoot-cell ${isWin ? 'tfoot-winner' : ''}">
                <span class="tfoot-total-price">${priceText}</span>
                <span class="tfoot-total-count">${pharm.availableCount}/${receta.length} disp</span>
              </td>
            `;
          }).join('')}
        </tr>
      </tfoot>
    </table>
  `;

  matrixWrapper.innerHTML = tableHtml;
  pharmacyGrid.appendChild(matrixWrapper);
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

  const normalizedQuery = rawQuery.toLowerCase();
  const invalidPhrases = [
    "ingresa los medicamentos",
    "separados por coma",
    "compara precios",
    "maximo 5 medicamentos",
    "maximo 10 medicamentos",
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

  resultsWrapper.style.display = "none";
  startWaitingAnimation(rawQuery);
  searchBtn.disabled = true;

  try {
    const encodedQuery = encodeURIComponent(queryItems.join(","));
    const response = await fetch(`${API}/api/buscar-receta?q=${encodedQuery}`);

    if (!response.ok) {
      throw new Error(`Error en el servidor (${response.status})`);
    }

    const data = await response.json();
    stopWaitingAnimation();

    if (data.receta && data.receta.length > 0) {
      renderRecipeComparison(data.receta, queryItems);
    } else {
      showErrorStatus("No se encontraron resultados para los medicamentos ingresados.");
    }
  } catch (err) {
    console.error(err);
    stopWaitingAnimation();
    showErrorStatus("No fue posible conectar con el servidor. Intenta nuevamente.");
  }
});
