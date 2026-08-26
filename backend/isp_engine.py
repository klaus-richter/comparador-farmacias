import os
import json
import re
import unicodedata
from typing import Optional, Dict, Any, List, Tuple

DICT_PATH = os.path.join(os.path.dirname(__file__), "data", "isp_dictionary.json")

FORM_CATEGORIES = {
    "nasal": {
        "keywords": ["nasal", "spray", "inhalador", "nebulizador", "puff", "dosis", "aerosol", "gotas nasales"],
        "conflicts": ["crema", "gel", "pomada", "unguento", "dermico", "dermica", "comprimidos", "capsulas", "jarabe", "ovulos"]
    },
    "crema": {
        "keywords": ["crema", "unguento", "pomada", "dermico", "dermica", "gel", "emulgel", "topico", "topica"],
        "conflicts": ["nasal", "spray", "jarabe", "comprimidos", "capsulas", "gotas", "inhalador", "ovulos"]
    },
    "gel": {
        "keywords": ["gel", "emulgel", "topico", "topica", "crema", "unguento"],
        "conflicts": ["nasal", "jarabe", "comprimidos", "capsulas", "gotas", "inhalador"]
    },
    "jarabe": {
        "keywords": ["jarabe", "suspension", "solucion oral", "elixir"],
        "conflicts": ["comprimidos", "capsulas", "crema", "gel", "pomada", "unguento", "spray", "nasal", "ovulos"]
    },
    "gotas": {
        "keywords": ["gotas", "solucion oral", "solucion oftalmica", "oftalmico", "otico", "colirio"],
        "conflicts": ["comprimidos", "capsulas", "crema", "pomada", "unguento"]
    },
    "comprimidos": {
        "keywords": ["comprimidos", "capsulas", "tabletas", "grajeas", "comp", "sobres", "caps", "recubiertos"],
        "conflicts": ["jarabe", "crema", "gel", "pomada", "unguento", "spray", "nasal", "gotas"]
    }
}

class ISPEngine:
    def __init__(self, dict_path: Optional[str] = None):
        path = dict_path or DICT_PATH
        self.data: Dict[str, Any] = {}
        self.principios_activos: Dict[str, Any] = {}
        self.marcas_a_principio: Dict[str, str] = {}
        
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                raw_activos = raw_data.get("principios_activos", {})
                
                for k, v in raw_activos.items():
                    norm_k = self.normalize(k)
                    norm_marcas = [self.normalize(m) for m in v.get("marcas", [])]
                    v_clean = dict(v)
                    v_clean["key_original"] = k
                    v_clean["marcas_norm"] = norm_marcas
                    self.principios_activos[norm_k] = v_clean
                    
                    self.marcas_a_principio[norm_k] = norm_k
                    for m in norm_marcas:
                        self.marcas_a_principio[m] = norm_k

    @staticmethod
    def normalize(text: str) -> str:
        if not text:
            return ""
        t = text.lower().strip()
        t = re.sub(r'(\d+)\s*(mg|mcg|g|ml|comp|comprimidos|capsulas|sobres)', r'\1 \2', t)
        nfkd = unicodedata.normalize('NFD', t)
        t = "".join([c for c in nfkd if unicodedata.category(c) != 'Mn'])
        t = t.replace('y', 'i').replace('v', 'b').replace('z', 's')
        t = re.sub(r'[^\w\s]', ' ', t)
        return re.sub(r'\s+', ' ', t).strip()

    def resolve_term(self, term: str) -> Dict[str, Any]:
        norm = self.normalize(term)
        words = norm.split()
        
        for length in range(len(words), 0, -1):
            for i in range(len(words) - length + 1):
                candidate = " ".join(words[i:i+length])
                
                if candidate in self.principios_activos:
                    info = self.principios_activos[candidate]
                    return {
                        "encontrado": True,
                        "tipo": "PRINCIPIO_ACTIVO",
                        "termino_buscado": term,
                        "principio_activo": info.get("key_original", candidate),
                        "nombre_oficial": info.get("nombre_oficial", candidate),
                        "clase_terapeutica": info.get("clase_terapeutica", ""),
                        "bioequivalente": info.get("bioequivalente", False)
                    }

                if candidate in self.marcas_a_principio:
                    p_norm_key = self.marcas_a_principio[candidate]
                    info = self.principios_activos.get(p_norm_key, {})
                    return {
                        "encontrado": True,
                        "tipo": "MARCA_COMERCIAL",
                        "termino_buscado": term,
                        "marca_identificada": candidate,
                        "principio_activo": info.get("key_original", p_norm_key),
                        "nombre_oficial": info.get("nombre_oficial", p_norm_key),
                        "clase_terapeutica": info.get("clase_terapeutica", ""),
                        "bioequivalente": info.get("bioequivalente", False)
                    }

        return {
            "encontrado": False,
            "tipo": "DESCONOCIDO",
            "termino_buscado": term,
            "principio_activo": None
        }

    def match_product_against_query(self, product_name: str, search_query: str) -> Tuple[bool, str]:
        norm_prod = self.normalize(product_name)
        norm_query = self.normalize(search_query)

        q_tokens = [t for t in norm_query.split() if len(t) >= 2]
        
        # 1. CANDADO DE DOSIS MÉDICA (Rechaza 50 cuando se pide 100)
        query_nums = [t for t in q_tokens if t.isdigit()]
        if query_nums:
            prod_nums = re.findall(r'\b\d+\b', norm_prod)
            if not any(num in prod_nums for num in query_nums):
                return False, "MISMATCH_DOSIS"

        # 2. CANDADO DE FORMA FARMACÉUTICA (Rechaza crema cuando se pide nasal)
        for form_key, form_info in FORM_CATEGORIES.items():
            if form_key in norm_query or any(kw in norm_query.split() for kw in form_info["keywords"]):
                prod_tokens = norm_prod.split()
                if any(cf in prod_tokens or cf in norm_prod for cf in form_info["conflicts"]):
                    return False, f"MISMATCH_FORMA_CONFLICTO ({form_key})"
                if not any(kw in norm_prod for kw in form_info["keywords"]):
                    return False, f"MISMATCH_FORMA_FALTA ({form_key})"

        # 3. MATCH INCLUSIVO: Si pasó los candados médicos, es un producto válido retornado por la farmacia
        return True, "MATCH_VALIDO"

isp_engine = ISPEngine()
