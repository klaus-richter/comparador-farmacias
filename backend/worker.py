import asyncio
import time
from typing import List, Optional
from backend.cache import (
    get_cached_results,
    save_cached_results,
    get_cache_stats,
    get_all_known_queries,
    clear_expired
)
from backend.scrapers_coordinator import scrapear_todas_las_farmacias

# Lista base limpia y deduplicada de medicamentos típicos en Chile
MEDICAMENTOS_TIPICOS = [
    "Paracetamol",
    "Ibuprofeno",
    "Losartan",
    "Ketorolaco",
    "Clorfenamina",
    "Diclofenaco",
    "Enalapril",
    "Loperamida",
    "Famotidina",
    "Naproxeno",
    "Acido Mefenamico",
    "Ciprofloxacina",
    "Loratadina",
    "Ketoprofeno",
    "Trimebutina",
    "Migranol",
    "Rupatadina",
    "Desloratadina",
    "Avamys",
    "Muno masticable",
    "Abrilar",
    "Eutirox",
    "Anilera",
    "Omeprazol",
    "Pregabalina",
    "Metformina",
    "Atorvastatina",
    "Zopiclona",
    "Clonazepam",
    "Sertralina",
    "Viadil",
    "Amoxicilina",
    "Cefalmin",
    "Fluoxetina",
    "Escitalopram",
    "Quetiapina",
    "Melatonina",
    "Amlodipino",
    "Celecoxib",
    "Meloxicam",
    "Tramadol",
    "Metamizol Sodico",
    "Aspirina Prevent",
    "Nefersil",
    "Alprazolam",
    "Amitriptilina",
    "Aradix",
    "Carvedilol",
    "Glibenclamida",
    "Furosemida",
    "Hidroclorotiazida",
    "Rosuvastatina",
    "Ezetimiba",
    "Omega 3",
    "Elcal D",
    "Vitamina D3",
    "Magnesio",
    "Vitamina C",
    "Colageno Hidrolizado",
    "Multibion",
    "Citracal Max",
    "Biotina",
    "Propoleo",
    "Probioticos",
    "Lanzoprazol",
    "Domperidona",
    "Bicarbonato de Sodio",
    "Esomeprazol",
    "Cetirizina",
    "Levocetirizina",
    "Salbutamol",
    "Fluticasona",
    "Prednisona",
    "Ambroxol",
    "Pseudoefedrina",
    "Azitromicina",
    "Nitrofurantoina",
    "Cefadroxilo",
    "Fluconazol",
    "Nistatina",
    "Levotiroxina",
    "Anulette",
    "Acotol",
    "Femelle",
    "Evra",
    "Progesterona",
    "Estradiol",
    "Ozempic",
    "Finasteride",
    "Dutasteride",
    "Minoxidil",
    "Tretinoina",
    "Aciclovir",
    "Betametasona",
    "Metronidazol",
    "Espironolactona",
    "Atropina",
    "Alcohol Gel",
    "Agua Oxigenada",
    "Suero Fisiologico",
    "Glicerina",
    "Lagrimas Artificiales",
    "Cloruro de Magnesio",
    "Glucosamina",
    "Lidocaina",
    "Tapsin",
    "Nastizol",
    "Trioval",
    "Kitadol",
    "Armonyl",
    "Povidona",
    "Lertus",
    "Dualten",
    "Bagoleta",
    "Diaren",
    "Geniol",
    "Aerogastrol",
    "Debridat",
    "Plidan",
    "Bion 3",
    "Neurobion",
    "Berocca",
    "Ensure",
    "Glucerna",
    "Cicatricure",
    "Hipoglos",
    "Glafornil",
    "Trayenta",
    "Jardiance",
    "Forxiga",
    "Januvia",
    "Lipangio",
    "Rowatinex",
    "Rowachol",
    "Bladuril",
    "Pirium",
    "Cranberry",
    "Urodem",
    "Ciproval",
    "Macrodantina",
    "Zinnat",
    "Clavinex",
    "Optamox",
    "Graneodin",
    "Faringol",
    "Tirodril",
    "Clotrimazol",
    "Terbinafina",
    "Dermabiotic",
    "Quadriderm",
    "Baycuten",
    "Lamisil",
    "Caladryl",
    "Lactulosa",
    "Dulcolax",
    "Ciruelax",
    "Ravotril",
    "Alplax",
    "Gamalate",
    "Mentholatum",
    "Palto Miel",
    "Nebulicina",
    "Rinofren",
    "Fisiolub",
    "Nasoneff",
    "Mometasona",
    "Budesonida",
    "Berodual",
    "Aerolin",
    "Atrovent",
    "Montelukast",
    "Zolpidem",
    "Eszopiclona",
    "Diazepam",
    "Lorazepam",
    "Bromazepam",
    "Claritromicina",
    "Clindamicina",
    "Doxiciclina",
    "Levofloxacino",
    "Cefalexina",
    "Amoval",
    "Betahistina",
    "Cinarizina",
    "Aldactone",
    "Atenolol",
    "Propranolol",
    "Spiriva",
    "Keppra",
    "Carbamazepina",
    "Acido Valproico",
    "Fenitoina",
    "Gabapentina",
    "Alopurinol",
    "Colchicina",
    "Cialis",
    "Pargeverina",
    "Buscapina",
    "Metoclopramida",
    "Sal de Andrews",
    "Disfruta",
    "Tapazol"
]

async def precargar_medicamentos(
    lista: Optional[List[str]] = None,
    delay_between: float = 1.0,
    force_refresh_all: bool = True
):
    """
    Worker diario (3:00 AM) para actualizar toda la base acumulada de medicamentos.
    Une los medicamentos típicos con todos los medicamentos que usuarios hayan buscado históricamente.
    """
    # Consolidar lista base + todo lo acumulado en la base de datos
    conocidos_bd = get_all_known_queries()
    todos_combinados = list(dict.fromkeys([m.strip() for m in (lista or (MEDICAMENTOS_TIPICOS + conocidos_bd)) if m.strip()]))
    
    print(f"=== INICIANDO WORKER DIARIO DE ACTUALIZACION ({len(todos_combinados)} medicamentos) ===")
    
    start_total = time.time()
    exitosos = 0
    fallidos = 0

    for idx, med in enumerate(todos_combinados, 1):
        print(f"[{idx}/{len(todos_combinados)}] [ACTUALIZANDO PRECIOS 3AM] '{med}'...")
        start_med = time.time()
        try:
            data = await scrapear_todas_las_farmacias(med, max_retries=2)
            save_cached_results(med, data)
            elapsed = round(time.time() - start_med, 2)
            exitosos += 1
            cob = data.get("cobertura", {})
            print(f"  -> [OK] '{med}': {data['total']} ofertas actualizadas en {elapsed}s | Cobertura: {cob.get('con_stock', 0)}/5 con stock")
        except Exception as e:
            fallidos += 1
            print(f"  -> [ERROR] Fallo al actualizar '{med}': {e}")

        if idx < len(todos_combinados) and delay_between > 0:
            await asyncio.sleep(delay_between)

    elapsed_total = round((time.time() - start_total) / 60, 2)
    stats = get_cache_stats()
    print(f"\n=== ACTUALIZACION MATUTINA COMPLETADA en {elapsed_total} minutos ===")
    print(f"Exitosos: {exitosos} | Errores: {fallidos}")
    print(f"Estado de la Base de Datos SQLite: {stats}")

if __name__ == "__main__":
    asyncio.run(precargar_medicamentos())
