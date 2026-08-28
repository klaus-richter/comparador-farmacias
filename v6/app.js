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
let stepInterval = null;
let currentPercent = 0;

function startWaitingAnimation(query) {
  statusBar.style.display = "flex";
  statusBar.className = "status-bar info";
  spinner.style.display = "block";
  currentPercent = 15;
  
  statusTitle.innerHTML = `Buscando medicamentos... <span class="progress-pct" id="progress-pct">15%</span>`;
  
  const fillEl = document.getElementById("progress-fill");
  if (fillEl) fillEl.style.width = "15%";

  let stepIndex = 0;
  statusStep.textContent = DYNAMIC_STEPS[0];
  statusStep.style.opacity = 1;

  if (progressInterval) clearInterval(progressInterval);
  if (stepInterval) clearInterval(stepInterval);

  // Progreso dinámico y rápido calibrado a los nuevos tiempos (avanza cada 450ms)
  progressInterval = setInterval(() => {
    if (currentPercent < 50) {
      currentPercent += Math.floor(Math.random() * 5) + 4; // Rápido al inicio
    } else if (currentPercent < 80) {
      currentPercent += Math.floor(Math.random() * 4) + 2; // Medio
    } else if (currentPercent < 95) {
      currentPercent += Math.floor(Math.random() * 2) + 1; // Suave hacia el 95%
    }
    if (currentPercent > 95) currentPercent = 95;

    const pctEl = document.getElementById("progress-pct");
    if (pctEl) pctEl.textContent = `${currentPercent}%`;

    const fillEl = document.getElementById("progress-fill");
    if (fillEl) fillEl.style.width = `${currentPercent}%`;
  }, 450);

  // Rotar textos informativos cada 2.8 segundos
  stepInterval = setInterval(() => {
    stepIndex = (stepIndex + 1) % DYNAMIC_STEPS.length;
    statusStep.style.opacity = 0;
    setTimeout(() => {
      statusStep.textContent = DYNAMIC_STEPS[stepIndex];
      statusStep.style.opacity = 1;
    }, 150);
  }, 2800);
}

function stopWaitingAnimation() {
  if (progressInterval) { 
    clearInterval(progressInterval); 
    progressInterval = null; 
  }
  if (stepInterval) {
    clearInterval(stepInterval);
    stepInterval = null;
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
  // 1. Usar motor semántico del ISP como fuente ÚNICA de verdad si está disponible
  if (typeof window !== "undefined" && window.ISPEngine) {
    return window.ISPEngine.matchProductAgainstQuery(prodName, searchQuery);
  }

  // 2. Fallback heurístico léxico (SOLO si el motor no cargó por algún motivo)
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
    .filter(item => parsePriceToNumber(item.precio) !== Infinity)
    .sort((a, b) => parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio));

  if (items.length === 0) return null;

  // TIER 1: Coincidencia inteligente usando el motor del ISP
  const exactMatches = items.filter(item => matchProductInteligente(item.nombre, searchProd));
  if (exactMatches.length > 0) {
    exactMatches.sort((a, b) => {
      const normQ = normalizeSearchText(searchProd).split(/\s+/);

      // Penalizacion Inteligente de "Apellidos" y Variantes
      if (normQ.length > 0) {
        const firstWord = normQ[0];
        let isPA = false;
        if (typeof ISP_DATA !== 'undefined' && ISP_DATA.principios_activos) {
           const paKeys = Object.keys(ISP_DATA.principios_activos);
           if (paKeys.some(pa => pa.includes(firstWord) || firstWord.includes(pa))) {
              isPA = true;
           }
        }
        
        const UNWANTED_MODIFIERS = ['infantil', 'pediatrico', 'pediátrico', 'jarabe', 'gotas', 'suspension', 'supositorios', 'fol', 'forte', 'plus', 'sr', 'xr', 'lp', 'cd', 'ap', 'd', 'c', 'dia', 'noche', 'mujer', 'hombre'];
        const ignoreList = ['mg', 'mcg', 'g', 'ml', 'ui', 'u', 'comp', 'comprimidos', 'capsulas', 'grageas', 'jeringas', 'ampollas', 'sobres', 'x', 'cm', 'l', 'recubiertos', 'recubierto'];
        
        const getPenaltyScore = (prodName) => {
           let penalty = 0;
           const words = normalizeSearchText(prodName).split(/\s+/);
           
           // Construir set de principios activos conocidos para no penalizarlos
           let knownPA = new Set();
           if (typeof ISP_DATA !== 'undefined' && ISP_DATA.principios_activos) {
             Object.keys(ISP_DATA.principios_activos).forEach(pa => {
               pa.split(/\s+/).forEach(w => knownPA.add(w));
             });
           }
           
           words.forEach(w => {
             if (normQ.includes(w)) return; // Si el usuario lo pidió explícitamente, no hay penalidad
             if (ignoreList.includes(w)) return; // Ignorar unidades de medida
             if (knownPA.has(w)) return; // No penalizar principios activos conocidos (ej: "levotiroxina" junto a "eutirox")
             if (w.length <= 2) return; // Ignorar palabras muy cortas (conectores, etc.)
             
             // Castigo severo SOLO para modificadores que cambian el tipo de droga/paciente
             if (UNWANTED_MODIFIERS.includes(w)) {
                penalty += 100000;
             } else if (!isPA) {
               // Penalización suave para palabras extra en marcas (contexto farmacéutico legítimo)
               if (/^\d+$/.test(w)) penalty += 2000;
               else penalty += 5000;
             }
           });
           return penalty;
        };

        const scoreA = getPenaltyScore(a.nombre);
        const scoreB = getPenaltyScore(b.nombre);

        if (scoreA !== scoreB) {
           return scoreA - scoreB;
        }
      }
      return parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio);
    });
    return exactMatches[0];
  }

  // TIER 2: Fallback Inteligente a Bioequivalente / Principio Activo
  // Si la farmacia no tiene la marca exacta, busca el principio activo equivalente respetando dosis y forma.
  const normQuery = normalizeSearchText(searchProd);
  const queryNums = normQuery.split(/\s+/).filter(tok => /^\d+$/.test(tok));
  
  let fallbackCandidates = [];
  
  // 1. Intentar resolver la marca a Principio Activo oficial ISP
  let paTerm = null;
  if (typeof window !== "undefined" && window.ISPEngine && window.ISPEngine.resolveTerm) {
    const res = window.ISPEngine.resolveTerm(searchProd);
    if (res && res.encontrado && res.principio_activo) {
      paTerm = normalizeSearchText(res.principio_activo);
    }
  }

  if (paTerm) {
    fallbackCandidates = items.filter(item => {
      const np = normalizeSearchText(item.nombre);
      // Debe contener el principio activo
      if (!np.includes(paTerm)) return false;
      // Debe respetar dosis si se especificó
      if (queryNums.length > 0) {
        const prodNums = np.match(/\b\d+\b/g) || [];
        if (!queryNums.some(num => prodNums.includes(num))) return false;
      }
      return true;
    });
  }

  // 2. Si no se resolvió por ISP pero hay dosis, buscar coincidencia estricta de dosis
  if (fallbackCandidates.length === 0 && queryNums.length > 0) {
    fallbackCandidates = items.filter(item => {
      const np = normalizeSearchText(item.nombre);
      const prodNums = np.match(/\b\d+\b/g) || [];
      return queryNums.some(num => prodNums.includes(num));
    });
  }

  if (fallbackCandidates.length > 0) {
    fallbackCandidates.sort((a, b) => parsePriceToNumber(a.precio) - parsePriceToNumber(b.precio));
    return fallbackCandidates[0];
  }

  // Si no hay coincidencias de marca ni principio activo/dosis, marcar Sin Stock
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
          #${idx + 1}
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

function showSearchBannerAlert(msg, isCooldown = false, seconds = 15) {
  const existing = document.getElementById("search-validation-banner");
  if (existing) existing.remove();

  const banner = document.createElement("div");
  banner.id = "search-validation-banner";
  
  if (isCooldown) {
    banner.style.cssText = "background: #eff6ff; border: 1.5px solid #bfdbfe; color: #1d4ed8; padding: 10px 16px; border-radius: 10px; font-weight: 700; font-size: 0.92rem; margin: 14px auto; max-width: 600px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 3px 10px rgba(29, 78, 216, 0.06);";
    let rem = seconds;
    banner.innerHTML = `<span>⏳</span> <span>Espera <b>${rem}s</b> antes de volver a buscar.</span>`;
    searchBtn.disabled = true;
    
    const interval = setInterval(() => {
      rem--;
      if (rem <= 0) {
        clearInterval(interval);
        banner.remove();
        searchBtn.disabled = false;
      } else {
        banner.innerHTML = `<span>⏳</span> <span>Espera <b>${rem}s</b> antes de volver a buscar.</span>`;
      }
    }, 1000);
  } else {
    banner.style.cssText = "background: #fef2f2; border: 1.5px solid #fecaca; color: #b91c1c; padding: 10px 16px; border-radius: 10px; font-weight: 700; font-size: 0.92rem; margin: 14px auto; max-width: 600px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 3px 10px rgba(239, 68, 68, 0.06);";
    banner.innerHTML = `<span>⚠️</span> <span>${msg}</span>`;
    setTimeout(() => {
      if (banner && banner.parentNode) banner.remove();
    }, 4000);
  }

  if (searchForm) {
    searchForm.insertAdjacentElement("afterend", banner);
  }
}

searchForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const rawQuery = searchInput.value.trim();
  if (!rawQuery) return;

  // 1. Candado Cooldown Anti-Spam (8 clics en 30s)
  if (!window._searchTimestamps) window._searchTimestamps = [];
  const now = Date.now();
  window._searchTimestamps = window._searchTimestamps.filter(t => now - t < 30000);
  if (window._searchTimestamps.length >= 8) {
    showSearchBannerAlert("", true, 15);
    return;
  }
  window._searchTimestamps.push(now);

  let queryItems = rawQuery.split(/[,;\n]+/).map(s => s.trim()).filter(Boolean);
  if (queryItems.length === 0) return;

  // 2. Candado Máximo 10 medicamentos por receta
  if (queryItems.length > 10) {
    showSearchBannerAlert("Máximo 10 medicamentos por receta.");
    return;
  }

  // 3. Validación de cada término
  const charRegex = /^[a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s\.\,\%\-\(\)\/]+$/;
  const letterRegex = /[a-zA-ZáéíóúñÁÉÍÓÚÑ]/g;

  for (let item of queryItems) {
    if (item.length > 50) {
      showSearchBannerAlert("Texto muy largo. Ingresa solo el nombre del medicamento.");
      return;
    }
    if (item.length < 2) {
      showSearchBannerAlert("Medicamento no válido. Revisa lo escrito.");
      return;
    }
    if (!charRegex.test(item)) {
      showSearchBannerAlert("Medicamento no válido. Revisa lo escrito.");
      return;
    }
    const letters = item.match(letterRegex);
    if (!letters || letters.length < 2) {
      showSearchBannerAlert("Medicamento no válido. Revisa lo escrito.");
      return;
    }
  }

  // Limpiar cualquier banner de error previo antes de buscar
  const prevBanner = document.getElementById("search-validation-banner");
  if (prevBanner) prevBanner.remove();

  const isMultiple = queryItems.length > 1;

  resultsWrapper.style.display = "none";
  startWaitingAnimation(rawQuery);
  searchBtn.disabled = true;
  searchBtn.querySelector(".btn-text").textContent = "Comparando...";

  const minWaitPromise = new Promise(resolve => setTimeout(resolve, 2000));

  try {
    const fetchPromise = fetch(`${API}/api/buscar-receta?q=${encodeURIComponent(queryItems.join(","))}`)
      .then(async res => {
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Error del servidor (HTTP ${res.status})`);
        }
        return await res.json();
      });
    const [data] = await Promise.all([fetchPromise, minWaitPromise]);
    if (data.status === "ok") { 
      stopWaitingAnimation(); 
      renderRecipeComparison(data.receta, queryItems); 
    }
  } catch (err) {
    stopWaitingAnimation();
    showSearchBannerAlert(err.message.replace(/^Error:\s*/i, ""));
  } finally {
    searchBtn.disabled = false;
    searchBtn.querySelector(".btn-text").textContent = "Comparar Farmacias";
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
