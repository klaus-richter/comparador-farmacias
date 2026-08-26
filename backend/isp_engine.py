import os
import json
import re
import unicodedata
from typing import Optional, Dict, Any, List, Tuple

DICT_PATH = os.path.join(os.path.dirname(__file__), "data", "isp_dictionary.json")

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
                        "marcas_registradas": info.get("marcas", []),
                        "dosis_comunes": info.get("dosis_comunes", []),
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
                        "marcas_hermanas": [m for m in info.get("marcas", []) if self.normalize(m) != candidate],
                        "dosis_comunes": info.get("dosis_comunes", []),
                        "bioequivalente": info.get("bioequivalente", False)
                    }

        return {
            "encontrado": False,
            "tipo": "DESCONOCIDO",
            "termino_buscado": term,
            "principio_activo": None,
            "marcas_registradas": []
        }

    def are_equivalent(self, term_a: str, term_b: str) -> bool:
        res_a = self.resolve_term(term_a)
        res_b = self.resolve_term(term_b)

        if res_a["encontrado"] and res_b["encontrado"]:
            return res_a["principio_activo"] == res_b["principio_activo"]

        norm_a = self.normalize(term_a)
        norm_b = self.normalize(term_b)
        return norm_a in norm_b or norm_b in norm_a

    def match_product_against_query(self, product_name: str, search_query: str) -> Tuple[bool, str]:
        norm_prod = self.normalize(product_name)
        norm_query = self.normalize(search_query)

        q_tokens = [t for t in norm_query.split() if len(t) >= 2]
        
        # CANDADO 1: GATEKEEPER ESTRICTO DE DOSIS MÉDICA
        # Si el usuario busca 'eutirox 100', el producto NO puede ser de 50mcg.
        query_nums = [t for t in q_tokens if t.isdigit()]
        if query_nums:
            prod_nums = re.findall(r'\b\d+\b', norm_prod)
            if not any(num in prod_nums for num in query_nums):
                return False, "MISMATCH_DOSIS"

        # 1. Match directo de palabras clave
        keywords = [t for t in q_tokens if not t.isdigit() and t not in ['comp', 'comprimidos', 'capsulas', 'mg', 'mcg']]
        if keywords and all(k in norm_prod for k in keywords):
            return True, "MATCH_TEXTO_DIRECTO"

        # 2. Match por Diccionario ISP
        q_info = self.resolve_term(search_query)
        if q_info["encontrado"]:
            norm_p_key = self.normalize(q_info["principio_activo"])
            if norm_p_key in norm_prod:
                return True, "MATCH_ISP_PRINCIPIO_ACTIVO"

            brands = self.principios_activos.get(norm_p_key, {}).get("marcas_norm", [])
            for b in brands:
                if b in norm_prod:
                    return True, f"MATCH_ISP_MARCA_EQUIVALENTE ({b})"

        return False, "NO_MATCH"

isp_engine = ISPEngine()
