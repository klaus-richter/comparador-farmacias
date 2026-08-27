// Diccionario Farmacéutico Oficial ISP Chile
// Puente Semántico para resolución de Marca -> Principio Activo
const ISP_DATA = {
  "version": "1.0.0",
  "pais": "Chile",
  "fuente_oficial": "Instituto de Salud Pública (ISP)",
  "total_principios_activos": 83,
  "total_marcas_indexadas": 539,
  "principios_activos": {
    "rupatadina": {
      "nombre_oficial": "Rupatadina",
      "clase_terapeutica": "Antihistamínico H1 de segunda generación",
      "marcas": [
        "rupax",
        "rexanel",
        "reax",
        "rupafin",
        "ruloxan",
        "rupatadina",
        "rupaler",
        "rinolast"
      ],
      "dosis_comunes": [
        "10 mg",
        "1 mg/ml"
      ],
      "formas": [
        "comprimidos",
        "solucion oral",
        "jarabe"
      ],
      "bioequivalente": true
    },
    "desloratadina": {
      "nombre_oficial": "Desloratadina",
      "clase_terapeutica": "Antihistamínico antialérgico",
      "marcas": [
        "despex",
        "d-histaplus",
        "d histaplus",
        "neo alledryl",
        "aerius",
        "tamides",
        "despeval",
        "desloratadina",
        "desalex",
        "rinofil",
        "desloran",
        "alercet d",
        "neodes"
      ],
      "dosis_comunes": [
        "5 mg",
        "2.5 mg/5ml",
        "0.5 mg/ml"
      ],
      "formas": [
        "comprimidos",
        "jarabe",
        "solucion oral"
      ],
      "bioequivalente": true
    },
    "levocetirizina": {
      "nombre_oficial": "Levocetirizina",
      "clase_terapeutica": "Antihistamínico antialérgico",
      "marcas": [
        "degraler",
        "xuzal",
        "alercet",
        "neolevocetirizina",
        "zival",
        "levorigotax",
        "levocetirizina",
        "alerziv"
      ],
      "dosis_comunes": [
        "5 mg",
        "2.5 mg/5ml",
        "5 mg/ml"
      ],
      "formas": [
        "comprimidos",
        "jarabe",
        "gotas orales"
      ],
      "bioequivalente": true
    },
    "cetirizina": {
      "nombre_oficial": "Cetirizina",
      "clase_terapeutica": "Antihistamínico antialérgico",
      "marcas": [
        "alerfast",
        "zyrtec",
        "cetirizina",
        "alergin",
        "histaler"
      ],
      "dosis_comunes": [
        "10 mg",
        "5 mg/5ml",
        "10 mg/ml"
      ],
      "formas": [
        "comprimidos",
        "jarabe",
        "gotas"
      ],
      "bioequivalente": true
    },
    "loratadina": {
      "nombre_oficial": "Loratadina",
      "clase_terapeutica": "Antihistamínico antialérgico",
      "marcas": [
        "clarityne",
        "alerpriv",
        "loratadina",
        "alerlis",
        "claritine",
        "histaplus"
      ],
      "dosis_comunes": [
        "10 mg",
        "5 mg/5ml"
      ],
      "formas": [
        "comprimidos",
        "jarabe"
      ],
      "bioequivalente": true
    },
    "clorfenamina": {
      "nombre_oficial": "Clorfenamina Maleato",
      "clase_terapeutica": "Antihistamínico H1 clásico",
      "marcas": [
        "clorfenamina",
        "cloroalergan",
        "polaramine",
        "alergan"
      ],
      "dosis_comunes": [
        "4 mg",
        "2 mg/5ml"
      ],
      "formas": [
        "comprimidos",
        "jarabe"
      ],
      "bioequivalente": true
    },
    "fexofenadina": {
      "nombre_oficial": "Fexofenadina Clorhidrato",
      "clase_terapeutica": "Antihistamínico",
      "marcas": [
        "allegra",
        "fexo",
        "altiva",
        "rinofed",
        "fexofenadina",
        "alermed"
      ],
      "dosis_comunes": [
        "120 mg",
        "180 mg",
        "60 mg",
        "30 mg/5ml"
      ],
      "formas": [
        "comprimidos recubiertos",
        "suspension"
      ],
      "bioequivalente": true
    },
    "hedera helix": {
      "nombre_oficial": "Hedera Helix (Extracto de Hoja de Hiedra)",
      "clase_terapeutica": "Mucolítico y expectorante bronquial",
      "marcas": [
        "abrilar",
        "paxel",
        "bronchopect",
        "hederix",
        "hedera helix",
        "prospan",
        "hiedrix",
        "hederavit",
        "toscalman",
        "hedera",
        "tussikind"
      ],
      "dosis_comunes": [
        "35 mg/5ml",
        "7 mg/ml"
      ],
      "formas": [
        "jarabe",
        "gotas orales",
        "pastillas efervescentes"
      ],
      "bioequivalente": true
    },
    "carbocisteina": {
      "nombre_oficial": "Carbocisteína",
      "clase_terapeutica": "Mucolítico y fluidificante",
      "marcas": [
        "broncotusilan",
        "mucolitico",
        "carbocisteina",
        "mucotos",
        "pectox"
      ],
      "dosis_comunes": [
        "100 mg/5ml",
        "250 mg/5ml",
        "120 ml",
        "100 ml"
      ],
      "formas": [
        "jarabe infantil",
        "jarabe adulto",
        "solucion oral"
      ],
      "bioequivalente": true
    },
    "ambroxol": {
      "nombre_oficial": "Ambroxol Clorhidrato",
      "clase_terapeutica": "Mucolítico expectorante",
      "marcas": [
        "mucosolvan",
        "ambroxol",
        "bronquisedan",
        "mucidren",
        "motivan"
      ],
      "dosis_comunes": [
        "15 mg/5ml",
        "30 mg/5ml",
        "30 mg"
      ],
      "formas": [
        "jarabe adulto",
        "jarabe infantil",
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "acetilcisteina": {
      "nombre_oficial": "Acetilcisteína",
      "clase_terapeutica": "Mucolítico",
      "marcas": [
        "flumil",
        "fluimucil",
        "acetilcisteina",
        "acemuk",
        "fludina",
        "mucomyst"
      ],
      "dosis_comunes": [
        "200 mg",
        "600 mg",
        "100 mg/5ml"
      ],
      "formas": [
        "sobres",
        "comprimidos efervescentes",
        "jarabe"
      ],
      "bioequivalente": true
    },
    "salbutamol": {
      "nombre_oficial": "Salbutamol Sulfato",
      "clase_terapeutica": "Broncodilatador agonista beta-2",
      "marcas": [
        "ventolin",
        "aerolin",
        "salbutral",
        "salbutamol",
        "butotal",
        "asmasal"
      ],
      "dosis_comunes": [
        "100 mcg",
        "200 dosis",
        "2 mg/5ml"
      ],
      "formas": [
        "aerosol para inhalacion",
        "jarabe",
        "nebulizacion"
      ],
      "bioequivalente": true
    },
    "budesonida": {
      "nombre_oficial": "Budesonida",
      "clase_terapeutica": "Corticoide inhalatorio y nasal",
      "marcas": [
        "pulmicort",
        "miflonide",
        "budesonida",
        "aerocort",
        "neplit",
        "rhinocort",
        "budecort"
      ],
      "dosis_comunes": [
        "200 mcg",
        "100 mcg",
        "0.5 mg/ml",
        "64 mcg",
        "32 mcg"
      ],
      "formas": [
        "inhalador bucal",
        "spray nasal",
        "suspension para nebulizar"
      ],
      "bioequivalente": true
    },
    "fluticasona": {
      "nombre_oficial": "Fluticasona Furoato / Propionato",
      "clase_terapeutica": "Corticoide antiinflamatorio nasal y bronquial",
      "marcas": [
        "avamys",
        "flixonase",
        "flixotide",
        "fluticasona",
        "plenair",
        "flixonex",
        "fluticort",
        "cutivate",
        "flutinex",
        "flutivate",
        "flusal",
        "brexotide"
      ],
      "dosis_comunes": [
        "27.5 mcg",
        "50 mcg",
        "120 dosis",
        "125 mcg",
        "250 mcg"
      ],
      "formas": [
        "spray nasal",
        "inhalador oral"
      ],
      "bioequivalente": true
    },
    "mometasona": {
      "nombre_oficial": "Mometasona Furoato",
      "clase_terapeutica": "Corticoide nasal y tópico",
      "marcas": [
        "nasonex",
        "mometasona",
        "unimom",
        "rinoval",
        "elocon",
        "pluster",
        "synaller",
        "suavicort",
        "proxona",
        "monez",
        "dimuxon",
        "momefast",
        "alermom",
        "dermosona"
      ],
      "dosis_comunes": [
        "50 mcg",
        "120 dosis",
        "140 dosis"
      ],
      "formas": [
        "spray nasal",
        "crema"
      ],
      "bioequivalente": true
    },
    "pseudoefedrina + clorfenamina": {
      "nombre_oficial": "Pseudoefedrina + Clorfenamina",
      "clase_terapeutica": "Descongestionante y antialérgico",
      "marcas": [
        "nastizol",
        "decongel",
        "nastizol compositum",
        "alerfedina",
        "rinocus"
      ],
      "dosis_comunes": [
        "60 mg / 4 mg",
        "comprimidos",
        "jarabe 100ml"
      ],
      "formas": [
        "comprimidos",
        "jarabe",
        "gotas"
      ],
      "bioequivalente": false
    },
    "paracetamol + pseudoefedrina + clorfenamina": {
      "nombre_oficial": "Paracetamol + Pseudoefedrina + Clorfenamina",
      "clase_terapeutica": "Antigripal descongestionante",
      "marcas": [
        "trioval",
        "tapsin dia y noche",
        "tapsin compuesto",
        "nastizol compuesto",
        "fludil",
        "antigripal",
        "viro grip",
        "winasorb"
      ],
      "dosis_comunes": [
        "comprimidos",
        "sobres calientes",
        "dia y noche"
      ],
      "formas": [
        "comprimidos",
        "sobres efervescentes"
      ],
      "bioequivalente": false
    },
    "paracetamol": {
      "nombre_oficial": "Paracetamol (Acetaminofén)",
      "clase_terapeutica": "Analgésico y antipirético",
      "marcas": [
        "kitadol",
        "tapsin",
        "gesidol",
        "panadol",
        "paracetamol",
        "dolagesic",
        "tempra",
        "tylenol",
        "acetaminofen",
        "parafast",
        "quitadol"
      ],
      "dosis_comunes": [
        "500 mg",
        "1 g",
        "1000 mg",
        "80 mg",
        "120 mg/5ml",
        "160 mg/5ml",
        "100 mg/ml"
      ],
      "formas": [
        "comprimidos",
        "gotas orales",
        "jarabe",
        "supositorios"
      ],
      "bioequivalente": true
    },
    "ibuprofeno": {
      "nombre_oficial": "Ibuprofeno",
      "clase_terapeutica": "Antiinflamatorio no esteroideo (AINE)",
      "marcas": [
        "advil",
        "motrin",
        "actron",
        "ibuprofeno",
        "dolven",
        "nurofen",
        "ibupirac",
        "febratic",
        "ibunova",
        "ipren"
      ],
      "dosis_comunes": [
        "400 mg",
        "600 mg",
        "800 mg",
        "200 mg",
        "100 mg/5ml",
        "200 mg/5ml"
      ],
      "formas": [
        "comprimidos recubiertos",
        "capsulas blandas",
        "suspension oral"
      ],
      "bioequivalente": true
    },
    "ketorolaco": {
      "nombre_oficial": "Ketorolaco Trometamol",
      "clase_terapeutica": "Analgésico AINE potente",
      "marcas": [
        "dolgenal",
        "ketorolaco",
        "analgex",
        "toradol",
        "algikey",
        "ketorolaco trometamina"
      ],
      "dosis_comunes": [
        "10 mg",
        "20 mg",
        "30 mg"
      ],
      "formas": [
        "comprimidos sublinguales",
        "comprimidos",
        "ampollas"
      ],
      "bioequivalente": true
    },
    "ketoprofeno": {
      "nombre_oficial": "Ketoprofeno",
      "clase_terapeutica": "Antiinflamatorio AINE",
      "marcas": [
        "talflex",
        "artrosil",
        "ketoprofeno",
        "profenid",
        "orudis",
        "ketoflam"
      ],
      "dosis_comunes": [
        "100 mg",
        "200 mg",
        "50 mg",
        "gel"
      ],
      "formas": [
        "comprimidos recubiertos",
        "capsulas de liberacion prolongada",
        "gel topico"
      ],
      "bioequivalente": true
    },
    "dexketoprofeno": {
      "nombre_oficial": "Dexketoprofeno Trometamol",
      "clase_terapeutica": "Analgésico AINE de acción rápida",
      "marcas": [
        "enantyum",
        "ketesse",
        "adolquir",
        "dexketoprofeno",
        "dexpro"
      ],
      "dosis_comunes": [
        "25 mg",
        "50 mg"
      ],
      "formas": [
        "comprimidos",
        "sobres granulados",
        "ampollas"
      ],
      "bioequivalente": true
    },
    "celecoxib": {
      "nombre_oficial": "Celecoxib",
      "clase_terapeutica": "Antiinflamatorio inhibidor selectivo COX-2",
      "marcas": [
        "celebrex",
        "celcox",
        "celebra",
        "celecoxib",
        "coxib",
        "valdyne"
      ],
      "dosis_comunes": [
        "100 mg",
        "200 mg"
      ],
      "formas": [
        "capsulas"
      ],
      "bioequivalente": true
    },
    "etoricoxib": {
      "nombre_oficial": "Etoricoxib",
      "clase_terapeutica": "Inhibidor selectivo COX-2",
      "marcas": [
        "arcoxia",
        "etoricoxib",
        "etoric",
        "exxiv",
        "coxitor",
        "torix"
      ],
      "dosis_comunes": [
        "60 mg",
        "90 mg",
        "120 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "meloxicam": {
      "nombre_oficial": "Meloxicam",
      "clase_terapeutica": "Antiinflamatorio AINE",
      "marcas": [
        "mobic",
        "meloxicam",
        "flamydol",
        "coxflam",
        "recox",
        "melox"
      ],
      "dosis_comunes": [
        "7.5 mg",
        "15 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "diclofenaco": {
      "nombre_oficial": "Diclofenaco Sódico / Potásico",
      "clase_terapeutica": "Antiinflamatorio y analgésico",
      "marcas": [
        "cataflam",
        "voltaren",
        "diclofenaco",
        "artren",
        "merpal",
        "diclogesic",
        "lertus",
        "deflox"
      ],
      "dosis_comunes": [
        "50 mg",
        "75 mg",
        "100 mg",
        "gel 1%",
        "gel 2%"
      ],
      "formas": [
        "comprimidos con recubrimiento enterico",
        "capsulas retard",
        "gel emulgel",
        "gotas"
      ],
      "bioequivalente": true
    },
    "tramadol": {
      "nombre_oficial": "Tramadol Clorhidrato",
      "clase_terapeutica": "Analgésico opioide atípico",
      "marcas": [
        "tramal",
        "tramadol",
        "zydol",
        "minidol",
        "adolan",
        "calmador"
      ],
      "dosis_comunes": [
        "50 mg",
        "100 mg",
        "100 mg/ml"
      ],
      "formas": [
        "capsulas",
        "gotas",
        "ampollas"
      ],
      "bioequivalente": true
    },
    "tramadol + paracetamol": {
      "nombre_oficial": "Tramadol + Paracetamol",
      "clase_terapeutica": "Analgésico combinado multimodal",
      "marcas": [
        "zaldiar",
        "tramacet",
        "patrol",
        "tramagesic",
        "minidol plus",
        "algidol"
      ],
      "dosis_comunes": [
        "37.5 mg / 325 mg",
        "75 mg / 650 mg"
      ],
      "formas": [
        "comprimidos recubiertos",
        "comprimidos efervescentes"
      ],
      "bioequivalente": true
    },
    "metamizol": {
      "nombre_oficial": "Metamizol Sódico (Dipirona)",
      "clase_terapeutica": "Analgésico y antipirético",
      "marcas": [
        "dipirona",
        "metamizol",
        "nolotil",
        "baralgina",
        "conmel",
        "fenalgina"
      ],
      "dosis_comunes": [
        "300 mg",
        "500 mg",
        "1 g",
        "250 mg/supositorio"
      ],
      "formas": [
        "comprimidos",
        "gotas orales",
        "supositorios",
        "ampollas"
      ],
      "bioequivalente": true
    },
    "naproxeno": {
      "nombre_oficial": "Naproxeno Sódico",
      "clase_terapeutica": "Antiinflamatorio no esteroideo",
      "marcas": [
        "flanax",
        "naprosyn",
        "naproxeno",
        "defron",
        "algesyst",
        "aleve",
        "apronax"
      ],
      "dosis_comunes": [
        "275 mg",
        "550 mg",
        "250 mg",
        "500 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "clonixinato de lisina": {
      "nombre_oficial": "Clonixinato de Lisina",
      "clase_terapeutica": "Analgésico",
      "marcas": [
        "dorixina",
        "nefrec",
        "clonixinato de lisina",
        "colmax",
        "dolalgial",
        "clonixin"
      ],
      "dosis_comunes": [
        "125 mg",
        "250 mg"
      ],
      "formas": [
        "comprimidos recubiertos",
        "ampollas"
      ],
      "bioequivalente": true
    },
    "pargeverina": {
      "nombre_oficial": "Pargeverina Clorhidrato",
      "clase_terapeutica": "Antiespasmódico visceral",
      "marcas": [
        "viadil",
        "pargeverina",
        "viadil compuesto",
        "plidan",
        "espasmo viadil"
      ],
      "dosis_comunes": [
        "10 mg",
        "5 mg/ml",
        "gotas 15ml"
      ],
      "formas": [
        "gotas orales",
        "comprimidos",
        "ampollas"
      ],
      "bioequivalente": true
    },
    "ácido acetilsalicílico": {
      "nombre_oficial": "Ácido Acetilsalicílico",
      "clase_terapeutica": "Antiagregante plaquetario y analgésico",
      "marcas": [
        "aspirina",
        "cardioaspirina",
        "coraspin",
        "aspirina infantil",
        "ecotrin",
        "aspirina 100",
        "aspirinetas"
      ],
      "dosis_comunes": [
        "100 mg",
        "500 mg",
        "81 mg"
      ],
      "formas": [
        "comprimidos",
        "comprimidos con recubrimiento enterico"
      ],
      "bioequivalente": true
    },
    "omeprazol": {
      "nombre_oficial": "Omeprazol",
      "clase_terapeutica": "Inhibidor de la bomba de protones (IBP)",
      "marcas": [
        "omeprazol",
        "losec",
        "gastridex",
        "lomex",
        "ascend",
        "omepral",
        "zomepral",
        "ulceral"
      ],
      "dosis_comunes": [
        "20 mg",
        "40 mg",
        "10 mg"
      ],
      "formas": [
        "capsulas con granulos con recubrimiento enterico",
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "esomeprazol": {
      "nombre_oficial": "Esomeprazol Magnésico",
      "clase_terapeutica": "Inhibidor de la bomba de protones",
      "marcas": [
        "nexium",
        "esomeprazol",
        "esoz",
        "esogastro",
        "cronocina",
        "esopran",
        "ezolium"
      ],
      "dosis_comunes": [
        "20 mg",
        "40 mg"
      ],
      "formas": [
        "comprimidos con recubrimiento enterico",
        "granulado"
      ],
      "bioequivalente": true
    },
    "pantoprazol": {
      "nombre_oficial": "Pantoprazol Sódico",
      "clase_terapeutica": "Inhibidor de la bomba de protones",
      "marcas": [
        "controloc",
        "pantoprazol",
        "pantocal",
        "zoltum",
        "pantozol"
      ],
      "dosis_comunes": [
        "20 mg",
        "40 mg"
      ],
      "formas": [
        "comprimidos con recubrimiento enterico"
      ],
      "bioequivalente": true
    },
    "lansoprazol": {
      "nombre_oficial": "Lansoprazol",
      "clase_terapeutica": "Inhibidor de la bomba de protones",
      "marcas": [
        "ogastro",
        "lansoprazol",
        "unival",
        "gastrotec",
        "lansolex"
      ],
      "dosis_comunes": [
        "15 mg",
        "30 mg"
      ],
      "formas": [
        "capsulas con microgranulos"
      ],
      "bioequivalente": true
    },
    "domperidona": {
      "nombre_oficial": "Domperidona",
      "clase_terapeutica": "Antiemético y procinético",
      "marcas": [
        "idom",
        "restol",
        "domperidona",
        "motilium",
        "vilidon",
        "nauzex"
      ],
      "dosis_comunes": [
        "10 mg",
        "1 mg/ml",
        "gotas 20ml"
      ],
      "formas": [
        "comprimidos",
        "gotas orales",
        "suspension"
      ],
      "bioequivalente": true
    },
    "metoclopramida": {
      "nombre_oficial": "Metoclopramida Clorhidrato",
      "clase_terapeutica": "Antiemético procinético",
      "marcas": [
        "plasil",
        "metoclopramida",
        "pimperan",
        "metoclopramida gotas"
      ],
      "dosis_comunes": [
        "10 mg",
        "2 mg/ml"
      ],
      "formas": [
        "comprimidos",
        "gotas",
        "ampollas"
      ],
      "bioequivalente": true
    },
    "trimebutina": {
      "nombre_oficial": "Trimebutina Maleato",
      "clase_terapeutica": "Regulador de motilidad intestinal (Colon irritable)",
      "marcas": [
        "debridat",
        "polibutin",
        "trimebutina",
        "colypan",
        "trim",
        "mutum"
      ],
      "dosis_comunes": [
        "100 mg",
        "200 mg",
        "300 mg"
      ],
      "formas": [
        "comprimidos",
        "comprimidos lp",
        "suspension"
      ],
      "bioequivalente": true
    },
    "simeticona": {
      "nombre_oficial": "Simeticona (Dimeticona activada)",
      "clase_terapeutica": "Antiflatulento",
      "marcas": [
        "aerored",
        "flapex",
        "simeticona",
        "factor ag",
        "gasorbis",
        "metigas"
      ],
      "dosis_comunes": [
        "40 mg",
        "80 mg",
        "125 mg",
        "gotas"
      ],
      "formas": [
        "comprimidos masticables",
        "gotas orales",
        "capsulas blandas"
      ],
      "bioequivalente": true
    },
    "magaldrato + simeticona": {
      "nombre_oficial": "Magaldrato + Simeticona",
      "clase_terapeutica": "Antiácido y antiflatulento",
      "marcas": [
        "riopan",
        "gastrogel",
        "acidex",
        "muno masticables",
        "almagel",
        "gelusil"
      ],
      "dosis_comunes": [
        "800 mg / 100 mg",
        "gel oral 200ml",
        "masticables"
      ],
      "formas": [
        "suspension oral",
        "comprimidos masticables"
      ],
      "bioequivalente": false
    },
    "probioticos": {
      "nombre_oficial": "Lactobacillus / Saccharomyces / Probióticos",
      "clase_terapeutica": "Restaurador de flora intestinal",
      "marcas": [
        "perenterol",
        "bioflore",
        "multiflora",
        "bion 3",
        "probiotix",
        "bagovital",
        "florestor",
        "lacteol"
      ],
      "dosis_comunes": [
        "capsulas",
        "sobres",
        "gotas"
      ],
      "formas": [
        "capsulas",
        "sobres en polvo"
      ],
      "bioequivalente": false
    },
    "losartan": {
      "nombre_oficial": "Losartán Potásico",
      "clase_terapeutica": "Antihipertensivo ARA-II",
      "marcas": [
        "cozaar",
        "losartan",
        "losapres",
        "simultan",
        "cardevas",
        "losartan potasico",
        "angioten"
      ],
      "dosis_comunes": [
        "50 mg",
        "100 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "enalapril": {
      "nombre_oficial": "Enalapril Maleato",
      "clase_terapeutica": "Antihipertensivo IECA",
      "marcas": [
        "renitec",
        "enalapril",
        "glioten",
        "lotensil",
        "enalapril maleato",
        "vasotec"
      ],
      "dosis_comunes": [
        "5 mg",
        "10 mg",
        "20 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "valsartan": {
      "nombre_oficial": "Valsartán",
      "clase_terapeutica": "Antihipertensivo ARA-II",
      "marcas": [
        "diovan",
        "valsartan",
        "valpress",
        "kalpress",
        "tareg",
        "valtan"
      ],
      "dosis_comunes": [
        "80 mg",
        "160 mg",
        "320 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "telmisartan": {
      "nombre_oficial": "Telmisartán",
      "clase_terapeutica": "Antihipertensivo ARA-II",
      "marcas": [
        "micardis",
        "telmisartan",
        "pritor",
        "actelsar",
        "telpres",
        "kinzal"
      ],
      "dosis_comunes": [
        "40 mg",
        "80 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "amlodipino": {
      "nombre_oficial": "Amlodipino Besilato",
      "clase_terapeutica": "Bloqueador de canales de calcio",
      "marcas": [
        "norvasc",
        "amlodipino",
        "amival",
        "plenacor",
        "ampliron",
        "coroval"
      ],
      "dosis_comunes": [
        "5 mg",
        "10 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "atenolol": {
      "nombre_oficial": "Atenolol",
      "clase_terapeutica": "Betabloqueador",
      "marcas": [
        "tenormin",
        "atenolol",
        "plenacor",
        "betacard",
        "atenolol"
      ],
      "dosis_comunes": [
        "50 mg",
        "100 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "bisoprolol": {
      "nombre_oficial": "Bisoprolol Fumarato",
      "clase_terapeutica": "Betabloqueador cardioselectivo",
      "marcas": [
        "concor",
        "bisoprolol",
        "corbis",
        "euradal",
        "bilol",
        "bisobloc"
      ],
      "dosis_comunes": [
        "1.25 mg",
        "2.5 mg",
        "5 mg",
        "10 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "carvedilol": {
      "nombre_oficial": "Carvedilol",
      "clase_terapeutica": "Betabloqueador alfa/beta",
      "marcas": [
        "dilatrend",
        "carvedilol",
        "carvedil",
        "dualten",
        "coreg"
      ],
      "dosis_comunes": [
        "6.25 mg",
        "12.5 mg",
        "25 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "hidroclorotiazida": {
      "nombre_oficial": "Hidroclorotiazida",
      "clase_terapeutica": "Diurético tiazídico",
      "marcas": [
        "hidroclorotiazida",
        "esidrex",
        "hctz",
        "diurace"
      ],
      "dosis_comunes": [
        "25 mg",
        "50 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "furosemida": {
      "nombre_oficial": "Furosemida",
      "clase_terapeutica": "Diurético de asa",
      "marcas": [
        "lasix",
        "furosemida",
        "edenol",
        "diurapid"
      ],
      "dosis_comunes": [
        "40 mg",
        "20 mg"
      ],
      "formas": [
        "comprimidos",
        "ampollas"
      ],
      "bioequivalente": true
    },
    "atorvastatina": {
      "nombre_oficial": "Atorvastatina Cálcica",
      "clase_terapeutica": "Hipolipemiante inhibidor HMG-CoA reductasa",
      "marcas": [
        "lipitor",
        "atorvastatina",
        "zarator",
        "ampliar",
        "cardyl",
        "torvast",
        "lipox"
      ],
      "dosis_comunes": [
        "10 mg",
        "20 mg",
        "40 mg",
        "80 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "rosuvastatina": {
      "nombre_oficial": "Rosuvastatina Cálcica",
      "clase_terapeutica": "Hipolipemiante estatina",
      "marcas": [
        "crestor",
        "rosuvastatina",
        "rovartal",
        "colestor",
        "rosuvast",
        "vivacor"
      ],
      "dosis_comunes": [
        "10 mg",
        "20 mg",
        "40 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "levotiroxina": {
      "nombre_oficial": "Levotiroxina Sódica",
      "clase_terapeutica": "Hormona tiroidea T4",
      "marcas": [
        "eutirox",
        "levotiroxina",
        "synthroid",
        "tirofil",
        "letrox",
        "levotiroxina sodica",
        "novothyral",
        "tiroxin",
        "t4"
      ],
      "dosis_comunes": [
        "25 mcg",
        "50 mcg",
        "75 mcg",
        "88 mcg",
        "100 mcg",
        "112 mcg",
        "125 mcg",
        "137 mcg",
        "150 mcg",
        "175 mcg",
        "200 mcg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "metformina": {
      "nombre_oficial": "Metformina Clorhidrato",
      "clase_terapeutica": "Antidiabético oral biguanida",
      "marcas": [
        "glaupax",
        "glucophage",
        "metformina",
        "hipoglucocin",
        "glifortex",
        "diaformin",
        "metfor",
        "stagid"
      ],
      "dosis_comunes": [
        "500 mg",
        "850 mg",
        "1000 mg",
        "750 mg xr",
        "1000 mg xr"
      ],
      "formas": [
        "comprimidos",
        "comprimidos de liberacion prolongada (xr)"
      ],
      "bioequivalente": true
    },
    "glibenclamida": {
      "nombre_oficial": "Glibenclamida",
      "clase_terapeutica": "Antidiabético sulfonilurea",
      "marcas": [
        "daonil",
        "glibenclamida",
        "euglucon",
        "gliben"
      ],
      "dosis_comunes": [
        "5 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "empagliflozina": {
      "nombre_oficial": "Empagliflozina",
      "clase_terapeutica": "Inhibidor SGLT2 antidiabético y cardiorrenal",
      "marcas": [
        "jardiance",
        "empagliflozina",
        "glyxambi"
      ],
      "dosis_comunes": [
        "10 mg",
        "25 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "dapagliflozina": {
      "nombre_oficial": "Dapagliflozina",
      "clase_terapeutica": "Inhibidor SGLT2",
      "marcas": [
        "forxiga",
        "dapagliflozina",
        "xigduo"
      ],
      "dosis_comunes": [
        "5 mg",
        "10 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "amoxicilina": {
      "nombre_oficial": "Amoxicilina Trihidrato",
      "clase_terapeutica": "Antibiótico betalactámico aminopenicilina",
      "marcas": [
        "amoval",
        "amoxicilina",
        "grunamox",
        "amobiotic",
        "ardine",
        "amoxil"
      ],
      "dosis_comunes": [
        "500 mg",
        "750 mg",
        "875 mg",
        "1000 mg",
        "250 mg/5ml",
        "500 mg/5ml"
      ],
      "formas": [
        "capsulas",
        "comprimidos",
        "suspension oral"
      ],
      "bioequivalente": true
    },
    "amoxicilina + acido clavulanico": {
      "nombre_oficial": "Amoxicilina + Ácido Clavulánico",
      "clase_terapeutica": "Antibiótico inhibidor de betalactamasas",
      "marcas": [
        "clavinex",
        "augmentin",
        "curam",
        "amoxicilina clavulanico",
        "bidamox",
        "clavamox",
        "clavinex duo"
      ],
      "dosis_comunes": [
        "500 mg / 125 mg",
        "875 mg / 125 mg",
        "400 mg / 57 mg / 5ml",
        "800 mg / 114 mg / 5ml"
      ],
      "formas": [
        "comprimidos recubiertos",
        "suspension oral forte"
      ],
      "bioequivalente": true
    },
    "azitromicina": {
      "nombre_oficial": "Azitromicina Dihidrato",
      "clase_terapeutica": "Antibiótico macrólido",
      "marcas": [
        "zitromax",
        "azitromicina",
        "trex",
        "azitrolit",
        "arzomicin",
        "azitrom"
      ],
      "dosis_comunes": [
        "500 mg",
        "200 mg/5ml"
      ],
      "formas": [
        "comprimidos recubiertos",
        "suspension oral"
      ],
      "bioequivalente": true
    },
    "ciprofloxacino": {
      "nombre_oficial": "Ciprofloxacino Clorhidrato",
      "clase_terapeutica": "Antibiótico fluoroquinolona",
      "marcas": [
        "cifloxin",
        "ciprofloxacino",
        "ciriax",
        "ciproval",
        "cipro",
        "quipro"
      ],
      "dosis_comunes": [
        "500 mg",
        "750 mg",
        "250 mg"
      ],
      "formas": [
        "comprimidos recubiertos",
        "gotas oftalmicas"
      ],
      "bioequivalente": true
    },
    "cefadroxilo": {
      "nombre_oficial": "Cefadroxilo Monohidrato",
      "clase_terapeutica": "Antibiótico cefalosporina de 1ra generación",
      "marcas": [
        "cefrin",
        "cefadroxilo",
        "bidroxyl",
        "droxil",
        "cefadur"
      ],
      "dosis_comunes": [
        "500 mg",
        "1 g",
        "250 mg/5ml",
        "500 mg/5ml"
      ],
      "formas": [
        "capsulas",
        "comprimidos",
        "suspension"
      ],
      "bioequivalente": true
    },
    "claritromicina": {
      "nombre_oficial": "Claritromicina",
      "clase_terapeutica": "Antibiótico macrólido",
      "marcas": [
        "klaricid",
        "claritromicina",
        "bactigram",
        "euromicina",
        "claricin"
      ],
      "dosis_comunes": [
        "500 mg",
        "250 mg",
        "125 mg/5ml",
        "250 mg/5ml"
      ],
      "formas": [
        "comprimidos recubiertos",
        "suspension"
      ],
      "bioequivalente": true
    },
    "nitrofurantoina": {
      "nombre_oficial": "Nitrofurantoína Macrocristales",
      "clase_terapeutica": "Antiséptico y antibacteriano urinario",
      "marcas": [
        "macrodantina",
        "nitrofurantoina",
        "furantoina",
        "uropol",
        "macrodin"
      ],
      "dosis_comunes": [
        "100 mg",
        "50 mg",
        "25 mg/5ml"
      ],
      "formas": [
        "capsulas",
        "suspension oral"
      ],
      "bioequivalente": true
    },
    "fluconazol": {
      "nombre_oficial": "Fluconazol",
      "clase_terapeutica": "Antifúngico triazólico",
      "marcas": [
        "diflucan",
        "fluconazol",
        "mutum",
        "flucostat",
        "micoflux"
      ],
      "dosis_comunes": [
        "150 mg",
        "200 mg",
        "50 mg"
      ],
      "formas": [
        "capsulas"
      ],
      "bioequivalente": true
    },
    "aciclovir": {
      "nombre_oficial": "Aciclovir",
      "clase_terapeutica": "Antiviral análogo de nucleósidos",
      "marcas": [
        "zovirax",
        "aciclovir",
        "etuvir",
        "herpex",
        "viralex",
        "poviral"
      ],
      "dosis_comunes": [
        "200 mg",
        "400 mg",
        "800 mg",
        "crema 5%"
      ],
      "formas": [
        "comprimidos",
        "crema dermica"
      ],
      "bioequivalente": true
    },
    "sertralina": {
      "nombre_oficial": "Sertralina Clorhidrato",
      "clase_terapeutica": "Antidepresivo ISRS",
      "marcas": [
        "zoloft",
        "sertralina",
        "altruline",
        "dominium",
        "eleval",
        "seronex",
        "sertral",
        "insertec"
      ],
      "dosis_comunes": [
        "50 mg",
        "100 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "escitalopram": {
      "nombre_oficial": "Escitalopram Oxalato",
      "clase_terapeutica": "Antidepresivo ISRS",
      "marcas": [
        "lexapro",
        "escitalopram",
        "ipran",
        "esertia",
        "rexit",
        "esitalex",
        "cipralex"
      ],
      "dosis_comunes": [
        "10 mg",
        "20 mg",
        "20 mg/ml"
      ],
      "formas": [
        "comprimidos recubiertos",
        "gotas orales"
      ],
      "bioequivalente": true
    },
    "fluoxetina": {
      "nombre_oficial": "Fluoxetina Clorhidrato",
      "clase_terapeutica": "Antidepresivo ISRS",
      "marcas": [
        "prozac",
        "fluoxetina",
        "ansium",
        "neupax",
        "daforin",
        "actan"
      ],
      "dosis_comunes": [
        "20 mg"
      ],
      "formas": [
        "capsulas",
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "clonazepam": {
      "nombre_oficial": "Clonazepam",
      "clase_terapeutica": "Ansiolítico y anticonvulsivante benzodiacepina",
      "marcas": [
        "rivotril",
        "clonazepam",
        "ravotril",
        "valpax",
        "neuryl",
        "clonex",
        "crismon"
      ],
      "dosis_comunes": [
        "0.5 mg",
        "1 mg",
        "2 mg",
        "2.5 mg/ml"
      ],
      "formas": [
        "comprimidos",
        "gotas orales sublinguales"
      ],
      "bioequivalente": true
    },
    "alprazolam": {
      "nombre_oficial": "Alprazolam",
      "clase_terapeutica": "Ansiolítico benzodiacepina",
      "marcas": [
        "xanax",
        "alprazolam",
        "adumbran",
        "tranquinal",
        "alpram",
        "calmosedan"
      ],
      "dosis_comunes": [
        "0.25 mg",
        "0.5 mg",
        "1 mg",
        "2 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "lorazepam": {
      "nombre_oficial": "Lorazepam",
      "clase_terapeutica": "Ansiolítico benzodiacepina",
      "marcas": [
        "ativan",
        "lorazepam",
        "amparax",
        "sedatival",
        "lorax"
      ],
      "dosis_comunes": [
        "1 mg",
        "2 mg"
      ],
      "formas": [
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "pregabalina": {
      "nombre_oficial": "Pregabalina",
      "clase_terapeutica": "Antiepiléptico y analgésico neuropático",
      "marcas": [
        "lyrica",
        "pregabalina",
        "plenica",
        "gabanet",
        "martesia",
        "neuroval",
        "prebictal"
      ],
      "dosis_comunes": [
        "25 mg",
        "50 mg",
        "75 mg",
        "150 mg",
        "300 mg"
      ],
      "formas": [
        "capsulas"
      ],
      "bioequivalente": true
    },
    "gabapentina": {
      "nombre_oficial": "Gabapentina",
      "clase_terapeutica": "Antineurálgico y antiepiléptico",
      "marcas": [
        "neurontin",
        "gabapentina",
        "dineurin",
        "gabictene"
      ],
      "dosis_comunes": [
        "300 mg",
        "400 mg",
        "600 mg",
        "800 mg"
      ],
      "formas": [
        "capsulas",
        "comprimidos"
      ],
      "bioequivalente": true
    },
    "zolpidem": {
      "nombre_oficial": "Zolpidem Hemitartrato",
      "clase_terapeutica": "Hipnótico no benzodiacepínico",
      "marcas": [
        "somno",
        "zolpidem",
        "nocte",
        "dormonid",
        "stilnox",
        "zolen"
      ],
      "dosis_comunes": [
        "10 mg",
        "5 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "vitamina d3": {
      "nombre_oficial": "Colecalciferol (Vitamina D3)",
      "clase_terapeutica": "Vitamina liposoluble fijadora de calcio",
      "marcas": [
        "colecalciferol",
        "vitamina d3",
        "deavit",
        "d-plen",
        "vides",
        "thorens",
        "d-vidol",
        "vitamina d"
      ],
      "dosis_comunes": [
        "800 ui",
        "1000 ui",
        "5000 ui",
        "25000 ui",
        "50000 ui",
        "100000 ui"
      ],
      "formas": [
        "capsulas blandas",
        "gotas orales",
        "frasco ampolla bebible"
      ],
      "bioequivalente": true
    },
    "complejo b": {
      "nombre_oficial": "Vitaminas Complejo B (B1, B6, B12)",
      "clase_terapeutica": "Neurotrófico vitamínico",
      "marcas": [
        "neurobionta",
        "nervobion",
        "bedoyecta",
        "vitamina b",
        "tiamina",
        "b-complejo",
        "dolo neurobionta"
      ],
      "dosis_comunes": [
        "comprimidos",
        "ampollas inyectables"
      ],
      "formas": [
        "comprimidos recubiertos",
        "solucion inyectable"
      ],
      "bioequivalente": false
    },
    "multivitaminico": {
      "nombre_oficial": "Multivitamínico con Minerales y Probióticos",
      "clase_terapeutica": "Suplemento alimentario",
      "marcas": [
        "bion 3",
        "centrum",
        "supradyn",
        "berocca",
        "pharmathon",
        "natabec",
        "nutrigel"
      ],
      "dosis_comunes": [
        "30 comprimidos",
        "60 comprimidos",
        "efervescente"
      ],
      "formas": [
        "comprimidos",
        "efervescentes",
        "capsulas"
      ],
      "bioequivalente": false
    },
    "sildenafil": {
      "nombre_oficial": "Sildenafil Citrato",
      "clase_terapeutica": "Inhibidor PDE5 para disfunción eréctil",
      "marcas": [
        "viagra",
        "sildenafil",
        "durafast",
        "eros",
        "plenis",
        "revatio",
        "sildefil"
      ],
      "dosis_comunes": [
        "50 mg",
        "100 mg"
      ],
      "formas": [
        "comprimidos masticables",
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    },
    "tadalafilo": {
      "nombre_oficial": "Tadalafilo",
      "clase_terapeutica": "Inhibidor PDE5 de acción prolongada",
      "marcas": [
        "cialis",
        "tadalafilo",
        "tudofil",
        "vigorrex",
        "tadax",
        "adcirca"
      ],
      "dosis_comunes": [
        "5 mg",
        "20 mg"
      ],
      "formas": [
        "comprimidos recubiertos"
      ],
      "bioequivalente": true
    }
  },
  "marcas_a_principio": {
    "rupatadina": "rupatadina",
    "rupax": "rupatadina",
    "rexanel": "rupatadina",
    "reax": "rupatadina",
    "rupafin": "rupatadina",
    "ruloxan": "rupatadina",
    "rupaler": "rupatadina",
    "rinolast": "rupatadina",
    "desloratadina": "desloratadina",
    "despex": "desloratadina",
    "d-histaplus": "desloratadina",
    "d histaplus": "desloratadina",
    "neo alledryl": "desloratadina",
    "aerius": "desloratadina",
    "tamides": "desloratadina",
    "despeval": "desloratadina",
    "desalex": "desloratadina",
    "rinofil": "desloratadina",
    "desloran": "desloratadina",
    "alercet d": "desloratadina",
    "neodes": "desloratadina",
    "levocetirizina": "levocetirizina",
    "degraler": "levocetirizina",
    "xuzal": "levocetirizina",
    "alercet": "levocetirizina",
    "neolevocetirizina": "levocetirizina",
    "zival": "levocetirizina",
    "levorigotax": "levocetirizina",
    "alerziv": "levocetirizina",
    "cetirizina": "cetirizina",
    "alerfast": "cetirizina",
    "zyrtec": "cetirizina",
    "alergin": "cetirizina",
    "histaler": "cetirizina",
    "loratadina": "loratadina",
    "clarityne": "loratadina",
    "alerpriv": "loratadina",
    "alerlis": "loratadina",
    "claritine": "loratadina",
    "histaplus": "loratadina",
    "clorfenamina": "clorfenamina",
    "cloroalergan": "clorfenamina",
    "polaramine": "clorfenamina",
    "alergan": "clorfenamina",
    "fexofenadina": "fexofenadina",
    "allegra": "fexofenadina",
    "fexo": "fexofenadina",
    "altiva": "fexofenadina",
    "rinofed": "fexofenadina",
    "alermed": "fexofenadina",
    "hedera helix": "hedera helix",
    "abrilar": "hedera helix",
    "paxel": "hedera helix",
    "bronchopect": "hedera helix",
    "hederix": "hedera helix",
    "prospan": "hedera helix",
    "hiedrix": "hedera helix",
    "hederavit": "hedera helix",
    "toscalman": "hedera helix",
    "hedera": "hedera helix",
    "tussikind": "hedera helix",
    "carbocisteina": "carbocisteina",
    "broncotusilan": "carbocisteina",
    "mucolitico": "carbocisteina",
    "mucotos": "carbocisteina",
    "pectox": "carbocisteina",
    "ambroxol": "ambroxol",
    "mucosolvan": "ambroxol",
    "bronquisedan": "ambroxol",
    "mucidren": "ambroxol",
    "motivan": "ambroxol",
    "acetilcisteina": "acetilcisteina",
    "flumil": "acetilcisteina",
    "fluimucil": "acetilcisteina",
    "acemuk": "acetilcisteina",
    "fludina": "acetilcisteina",
    "mucomyst": "acetilcisteina",
    "salbutamol": "salbutamol",
    "ventolin": "salbutamol",
    "aerolin": "salbutamol",
    "salbutral": "salbutamol",
    "butotal": "salbutamol",
    "asmasal": "salbutamol",
    "budesonida": "budesonida",
    "pulmicort": "budesonida",
    "miflonide": "budesonida",
    "aerocort": "budesonida",
    "neplit": "budesonida",
    "rhinocort": "budesonida",
    "budecort": "budesonida",
    "fluticasona": "fluticasona",
    "avamys": "fluticasona",
    "flixonase": "fluticasona",
    "flixotide": "fluticasona",
    "plenair": "fluticasona",
    "flixonex": "fluticasona",
    "fluticort": "fluticasona",
    "cutivate": "fluticasona",
    "flutinex": "fluticasona",
    "flutivate": "fluticasona",
    "flusal": "fluticasona",
    "brexotide": "fluticasona",
    "mometasona": "mometasona",
    "nasonex": "mometasona",
    "unimom": "mometasona",
    "rinoval": "mometasona",
    "elocon": "mometasona",
    "pluster": "mometasona",
    "synaller": "mometasona",
    "suavicort": "mometasona",
    "proxona": "mometasona",
    "monez": "mometasona",
    "dimuxon": "mometasona",
    "momefast": "mometasona",
    "alermom": "mometasona",
    "dermosona": "mometasona",
    "pseudoefedrina + clorfenamina": "pseudoefedrina + clorfenamina",
    "nastizol": "pseudoefedrina + clorfenamina",
    "decongel": "pseudoefedrina + clorfenamina",
    "nastizol compositum": "pseudoefedrina + clorfenamina",
    "alerfedina": "pseudoefedrina + clorfenamina",
    "rinocus": "pseudoefedrina + clorfenamina",
    "paracetamol + pseudoefedrina + clorfenamina": "paracetamol + pseudoefedrina + clorfenamina",
    "trioval": "paracetamol + pseudoefedrina + clorfenamina",
    "tapsin dia y noche": "paracetamol + pseudoefedrina + clorfenamina",
    "tapsin compuesto": "paracetamol + pseudoefedrina + clorfenamina",
    "nastizol compuesto": "paracetamol + pseudoefedrina + clorfenamina",
    "fludil": "paracetamol + pseudoefedrina + clorfenamina",
    "antigripal": "paracetamol + pseudoefedrina + clorfenamina",
    "viro grip": "paracetamol + pseudoefedrina + clorfenamina",
    "winasorb": "paracetamol + pseudoefedrina + clorfenamina",
    "paracetamol": "paracetamol",
    "kitadol": "paracetamol",
    "tapsin": "paracetamol",
    "gesidol": "paracetamol",
    "panadol": "paracetamol",
    "dolagesic": "paracetamol",
    "tempra": "paracetamol",
    "tylenol": "paracetamol",
    "acetaminofen": "paracetamol",
    "parafast": "paracetamol",
    "quitadol": "paracetamol",
    "ibuprofeno": "ibuprofeno",
    "advil": "ibuprofeno",
    "motrin": "ibuprofeno",
    "actron": "ibuprofeno",
    "dolven": "ibuprofeno",
    "nurofen": "ibuprofeno",
    "ibupirac": "ibuprofeno",
    "febratic": "ibuprofeno",
    "ibunova": "ibuprofeno",
    "ipren": "ibuprofeno",
    "ketorolaco": "ketorolaco",
    "dolgenal": "ketorolaco",
    "analgex": "ketorolaco",
    "toradol": "ketorolaco",
    "algikey": "ketorolaco",
    "ketorolaco trometamina": "ketorolaco",
    "ketoprofeno": "ketoprofeno",
    "talflex": "ketoprofeno",
    "artrosil": "ketoprofeno",
    "profenid": "ketoprofeno",
    "orudis": "ketoprofeno",
    "ketoflam": "ketoprofeno",
    "dexketoprofeno": "dexketoprofeno",
    "enantyum": "dexketoprofeno",
    "ketesse": "dexketoprofeno",
    "adolquir": "dexketoprofeno",
    "dexpro": "dexketoprofeno",
    "celecoxib": "celecoxib",
    "celebrex": "celecoxib",
    "celcox": "celecoxib",
    "celebra": "celecoxib",
    "coxib": "celecoxib",
    "valdyne": "celecoxib",
    "etoricoxib": "etoricoxib",
    "arcoxia": "etoricoxib",
    "etoric": "etoricoxib",
    "exxiv": "etoricoxib",
    "coxitor": "etoricoxib",
    "torix": "etoricoxib",
    "meloxicam": "meloxicam",
    "mobic": "meloxicam",
    "flamydol": "meloxicam",
    "coxflam": "meloxicam",
    "recox": "meloxicam",
    "melox": "meloxicam",
    "diclofenaco": "diclofenaco",
    "cataflam": "diclofenaco",
    "voltaren": "diclofenaco",
    "artren": "diclofenaco",
    "merpal": "diclofenaco",
    "diclogesic": "diclofenaco",
    "lertus": "diclofenaco",
    "deflox": "diclofenaco",
    "tramadol": "tramadol",
    "tramal": "tramadol",
    "zydol": "tramadol",
    "minidol": "tramadol",
    "adolan": "tramadol",
    "calmador": "tramadol",
    "tramadol + paracetamol": "tramadol + paracetamol",
    "zaldiar": "tramadol + paracetamol",
    "tramacet": "tramadol + paracetamol",
    "patrol": "tramadol + paracetamol",
    "tramagesic": "tramadol + paracetamol",
    "minidol plus": "tramadol + paracetamol",
    "algidol": "tramadol + paracetamol",
    "metamizol": "metamizol",
    "dipirona": "metamizol",
    "nolotil": "metamizol",
    "baralgina": "metamizol",
    "conmel": "metamizol",
    "fenalgina": "metamizol",
    "naproxeno": "naproxeno",
    "flanax": "naproxeno",
    "naprosyn": "naproxeno",
    "defron": "naproxeno",
    "algesyst": "naproxeno",
    "aleve": "naproxeno",
    "apronax": "naproxeno",
    "clonixinato de lisina": "clonixinato de lisina",
    "dorixina": "clonixinato de lisina",
    "nefrec": "clonixinato de lisina",
    "colmax": "clonixinato de lisina",
    "dolalgial": "clonixinato de lisina",
    "clonixin": "clonixinato de lisina",
    "pargeverina": "pargeverina",
    "viadil": "pargeverina",
    "viadil compuesto": "pargeverina",
    "plidan": "pargeverina",
    "espasmo viadil": "pargeverina",
    "ácido acetilsalicílico": "ácido acetilsalicílico",
    "aspirina": "ácido acetilsalicílico",
    "cardioaspirina": "ácido acetilsalicílico",
    "coraspin": "ácido acetilsalicílico",
    "aspirina infantil": "ácido acetilsalicílico",
    "ecotrin": "ácido acetilsalicílico",
    "aspirina 100": "ácido acetilsalicílico",
    "aspirinetas": "ácido acetilsalicílico",
    "omeprazol": "omeprazol",
    "losec": "omeprazol",
    "gastridex": "omeprazol",
    "lomex": "omeprazol",
    "ascend": "omeprazol",
    "omepral": "omeprazol",
    "zomepral": "omeprazol",
    "ulceral": "omeprazol",
    "esomeprazol": "esomeprazol",
    "nexium": "esomeprazol",
    "esoz": "esomeprazol",
    "esogastro": "esomeprazol",
    "cronocina": "esomeprazol",
    "esopran": "esomeprazol",
    "ezolium": "esomeprazol",
    "pantoprazol": "pantoprazol",
    "controloc": "pantoprazol",
    "pantocal": "pantoprazol",
    "zoltum": "pantoprazol",
    "pantozol": "pantoprazol",
    "lansoprazol": "lansoprazol",
    "ogastro": "lansoprazol",
    "unival": "lansoprazol",
    "gastrotec": "lansoprazol",
    "lansolex": "lansoprazol",
    "domperidona": "domperidona",
    "idom": "domperidona",
    "restol": "domperidona",
    "motilium": "domperidona",
    "vilidon": "domperidona",
    "nauzex": "domperidona",
    "metoclopramida": "metoclopramida",
    "plasil": "metoclopramida",
    "pimperan": "metoclopramida",
    "metoclopramida gotas": "metoclopramida",
    "trimebutina": "trimebutina",
    "debridat": "trimebutina",
    "polibutin": "trimebutina",
    "colypan": "trimebutina",
    "trim": "trimebutina",
    "mutum": "fluconazol",
    "simeticona": "simeticona",
    "aerored": "simeticona",
    "flapex": "simeticona",
    "factor ag": "simeticona",
    "gasorbis": "simeticona",
    "metigas": "simeticona",
    "magaldrato + simeticona": "magaldrato + simeticona",
    "riopan": "magaldrato + simeticona",
    "gastrogel": "magaldrato + simeticona",
    "acidex": "magaldrato + simeticona",
    "muno masticables": "magaldrato + simeticona",
    "almagel": "magaldrato + simeticona",
    "gelusil": "magaldrato + simeticona",
    "probioticos": "probioticos",
    "perenterol": "probioticos",
    "bioflore": "probioticos",
    "multiflora": "probioticos",
    "bion 3": "multivitaminico",
    "probiotix": "probioticos",
    "bagovital": "probioticos",
    "florestor": "probioticos",
    "lacteol": "probioticos",
    "losartan": "losartan",
    "cozaar": "losartan",
    "losapres": "losartan",
    "simultan": "losartan",
    "cardevas": "losartan",
    "losartan potasico": "losartan",
    "angioten": "losartan",
    "enalapril": "enalapril",
    "renitec": "enalapril",
    "glioten": "enalapril",
    "lotensil": "enalapril",
    "enalapril maleato": "enalapril",
    "vasotec": "enalapril",
    "valsartan": "valsartan",
    "diovan": "valsartan",
    "valpress": "valsartan",
    "kalpress": "valsartan",
    "tareg": "valsartan",
    "valtan": "valsartan",
    "telmisartan": "telmisartan",
    "micardis": "telmisartan",
    "pritor": "telmisartan",
    "actelsar": "telmisartan",
    "telpres": "telmisartan",
    "kinzal": "telmisartan",
    "amlodipino": "amlodipino",
    "norvasc": "amlodipino",
    "amival": "amlodipino",
    "plenacor": "atenolol",
    "ampliron": "amlodipino",
    "coroval": "amlodipino",
    "atenolol": "atenolol",
    "tenormin": "atenolol",
    "betacard": "atenolol",
    "bisoprolol": "bisoprolol",
    "concor": "bisoprolol",
    "corbis": "bisoprolol",
    "euradal": "bisoprolol",
    "bilol": "bisoprolol",
    "bisobloc": "bisoprolol",
    "carvedilol": "carvedilol",
    "dilatrend": "carvedilol",
    "carvedil": "carvedilol",
    "dualten": "carvedilol",
    "coreg": "carvedilol",
    "hidroclorotiazida": "hidroclorotiazida",
    "esidrex": "hidroclorotiazida",
    "hctz": "hidroclorotiazida",
    "diurace": "hidroclorotiazida",
    "furosemida": "furosemida",
    "lasix": "furosemida",
    "edenol": "furosemida",
    "diurapid": "furosemida",
    "atorvastatina": "atorvastatina",
    "lipitor": "atorvastatina",
    "zarator": "atorvastatina",
    "ampliar": "atorvastatina",
    "cardyl": "atorvastatina",
    "torvast": "atorvastatina",
    "lipox": "atorvastatina",
    "rosuvastatina": "rosuvastatina",
    "crestor": "rosuvastatina",
    "rovartal": "rosuvastatina",
    "colestor": "rosuvastatina",
    "rosuvast": "rosuvastatina",
    "vivacor": "rosuvastatina",
    "levotiroxina": "levotiroxina",
    "eutirox": "levotiroxina",
    "synthroid": "levotiroxina",
    "tirofil": "levotiroxina",
    "letrox": "levotiroxina",
    "levotiroxina sodica": "levotiroxina",
    "novothyral": "levotiroxina",
    "tiroxin": "levotiroxina",
    "t4": "levotiroxina",
    "metformina": "metformina",
    "glaupax": "metformina",
    "glucophage": "metformina",
    "hipoglucocin": "metformina",
    "glifortex": "metformina",
    "diaformin": "metformina",
    "metfor": "metformina",
    "stagid": "metformina",
    "glibenclamida": "glibenclamida",
    "daonil": "glibenclamida",
    "euglucon": "glibenclamida",
    "gliben": "glibenclamida",
    "empagliflozina": "empagliflozina",
    "jardiance": "empagliflozina",
    "glyxambi": "empagliflozina",
    "dapagliflozina": "dapagliflozina",
    "forxiga": "dapagliflozina",
    "xigduo": "dapagliflozina",
    "amoxicilina": "amoxicilina",
    "amoval": "amoxicilina",
    "grunamox": "amoxicilina",
    "amobiotic": "amoxicilina",
    "ardine": "amoxicilina",
    "amoxil": "amoxicilina",
    "amoxicilina + acido clavulanico": "amoxicilina + acido clavulanico",
    "clavinex": "amoxicilina + acido clavulanico",
    "augmentin": "amoxicilina + acido clavulanico",
    "curam": "amoxicilina + acido clavulanico",
    "amoxicilina clavulanico": "amoxicilina + acido clavulanico",
    "bidamox": "amoxicilina + acido clavulanico",
    "clavamox": "amoxicilina + acido clavulanico",
    "clavinex duo": "amoxicilina + acido clavulanico",
    "azitromicina": "azitromicina",
    "zitromax": "azitromicina",
    "trex": "azitromicina",
    "azitrolit": "azitromicina",
    "arzomicin": "azitromicina",
    "azitrom": "azitromicina",
    "ciprofloxacino": "ciprofloxacino",
    "cifloxin": "ciprofloxacino",
    "ciriax": "ciprofloxacino",
    "ciproval": "ciprofloxacino",
    "cipro": "ciprofloxacino",
    "quipro": "ciprofloxacino",
    "cefadroxilo": "cefadroxilo",
    "cefrin": "cefadroxilo",
    "bidroxyl": "cefadroxilo",
    "droxil": "cefadroxilo",
    "cefadur": "cefadroxilo",
    "claritromicina": "claritromicina",
    "klaricid": "claritromicina",
    "bactigram": "claritromicina",
    "euromicina": "claritromicina",
    "claricin": "claritromicina",
    "nitrofurantoina": "nitrofurantoina",
    "macrodantina": "nitrofurantoina",
    "furantoina": "nitrofurantoina",
    "uropol": "nitrofurantoina",
    "macrodin": "nitrofurantoina",
    "fluconazol": "fluconazol",
    "diflucan": "fluconazol",
    "flucostat": "fluconazol",
    "micoflux": "fluconazol",
    "aciclovir": "aciclovir",
    "zovirax": "aciclovir",
    "etuvir": "aciclovir",
    "herpex": "aciclovir",
    "viralex": "aciclovir",
    "poviral": "aciclovir",
    "sertralina": "sertralina",
    "zoloft": "sertralina",
    "altruline": "sertralina",
    "dominium": "sertralina",
    "eleval": "sertralina",
    "seronex": "sertralina",
    "sertral": "sertralina",
    "insertec": "sertralina",
    "escitalopram": "escitalopram",
    "lexapro": "escitalopram",
    "ipran": "escitalopram",
    "esertia": "escitalopram",
    "rexit": "escitalopram",
    "esitalex": "escitalopram",
    "cipralex": "escitalopram",
    "fluoxetina": "fluoxetina",
    "prozac": "fluoxetina",
    "ansium": "fluoxetina",
    "neupax": "fluoxetina",
    "daforin": "fluoxetina",
    "actan": "fluoxetina",
    "clonazepam": "clonazepam",
    "rivotril": "clonazepam",
    "ravotril": "clonazepam",
    "valpax": "clonazepam",
    "neuryl": "clonazepam",
    "clonex": "clonazepam",
    "crismon": "clonazepam",
    "alprazolam": "alprazolam",
    "xanax": "alprazolam",
    "adumbran": "alprazolam",
    "tranquinal": "alprazolam",
    "alpram": "alprazolam",
    "calmosedan": "alprazolam",
    "lorazepam": "lorazepam",
    "ativan": "lorazepam",
    "amparax": "lorazepam",
    "sedatival": "lorazepam",
    "lorax": "lorazepam",
    "pregabalina": "pregabalina",
    "lyrica": "pregabalina",
    "plenica": "pregabalina",
    "gabanet": "pregabalina",
    "martesia": "pregabalina",
    "neuroval": "pregabalina",
    "prebictal": "pregabalina",
    "gabapentina": "gabapentina",
    "neurontin": "gabapentina",
    "dineurin": "gabapentina",
    "gabictene": "gabapentina",
    "zolpidem": "zolpidem",
    "somno": "zolpidem",
    "nocte": "zolpidem",
    "dormonid": "zolpidem",
    "stilnox": "zolpidem",
    "zolen": "zolpidem",
    "vitamina d3": "vitamina d3",
    "colecalciferol": "vitamina d3",
    "deavit": "vitamina d3",
    "d-plen": "vitamina d3",
    "vides": "vitamina d3",
    "thorens": "vitamina d3",
    "d-vidol": "vitamina d3",
    "vitamina d": "vitamina d3",
    "complejo b": "complejo b",
    "neurobionta": "complejo b",
    "nervobion": "complejo b",
    "bedoyecta": "complejo b",
    "vitamina b": "complejo b",
    "tiamina": "complejo b",
    "b-complejo": "complejo b",
    "dolo neurobionta": "complejo b",
    "multivitaminico": "multivitaminico",
    "centrum": "multivitaminico",
    "supradyn": "multivitaminico",
    "berocca": "multivitaminico",
    "pharmathon": "multivitaminico",
    "natabec": "multivitaminico",
    "nutrigel": "multivitaminico",
    "sildenafil": "sildenafil",
    "viagra": "sildenafil",
    "durafast": "sildenafil",
    "eros": "sildenafil",
    "plenis": "sildenafil",
    "revatio": "sildenafil",
    "sildefil": "sildenafil",
    "tadalafilo": "tadalafilo",
    "cialis": "tadalafilo",
    "tudofil": "tadalafilo",
    "vigorrex": "tadalafilo",
    "tadax": "tadalafilo",
    "adcirca": "tadalafilo"
  }
};

const FORM_CATEGORIES = {
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
};

const ISPEngineClient = {
  normalize: function(text) {
    if (!text) return "";
    let t = text.toLowerCase().trim();
    t = t.replace(/(\d+)\s*(mg|mcg|g|ml|comp|comprimidos|capsulas|sobres)/gi, '$1 $2');
    t = t.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    t = t.replace(/y/g, 'i').replace(/v/g, 'b').replace(/z/g, 's');
    t = t.replace(/[^\w\s]/g, ' ');
    return t.replace(/\s+/g, ' ').trim();
  },

  resolveTerm: function(term) {
    const norm = this.normalize(term);
    const words = norm.split(/\s+/);
    const activos = ISP_DATA.principios_activos || {};
    const marcas = ISP_DATA.marcas_a_principio || {};

    for (let len = words.length; len >= 1; len--) {
      for (let i = 0; i <= words.length - len; i++) {
        const cand = words.slice(i, i + len).join(" ");
        
        for (const [k, info] of Object.entries(activos)) {
          if (this.normalize(k) === cand) {
            return {
              encontrado: true,
              tipo: "PRINCIPIO_ACTIVO",
              principio_activo: k,
              nombre_oficial: info.nombre_oficial || k,
              clase_terapeutica: info.clase_terapeutica || "",
              bioequivalente: info.bioequivalente || false
            };
          }
        }

        for (const [m, pKey] of Object.entries(marcas)) {
          if (this.normalize(m) === cand) {
            const info = activos[pKey] || {};
            return {
              encontrado: true,
              tipo: "MARCA_COMERCIAL",
              marca_identificada: m,
              principio_activo: pKey,
              nombre_oficial: info.nombre_oficial || pKey,
              clase_terapeutica: info.clase_terapeutica || "",
              bioequivalente: info.bioequivalente || false
            };
          }
        }
      }
    }

    return { encontrado: false, tipo: "DESCONOCIDO", principio_activo: null };
  },

  matchProductAgainstQuery: function(productName, searchQuery) {
    const normProd = this.normalize(productName);
    const normQuery = this.normalize(searchQuery);

    const qTokens = normQuery.split(/\s+/).filter(tok => tok.length >= 2);
    
    // 1. CANDADO DE DOSIS MÉDICA
    const queryNums = qTokens.filter(tok => /^\d+$/.test(tok));
    if (queryNums.length > 0) {
      const prodNums = normProd.match(/\b\d+\b/g) || [];
      if (!queryNums.some(num => prodNums.includes(num))) {
        return false;
      }
    }

    // 2. CANDADO DE FORMA FARMACÉUTICA
    for (const [formKey, formInfo] of Object.entries(FORM_CATEGORIES)) {
      if (normQuery.includes(formKey) || formInfo.keywords.some(kw => normQuery.split(/\s+/).includes(kw))) {
        const prodWords = normProd.split(/\s+/);
        if (formInfo.conflicts.some(cf => prodWords.includes(cf) || normProd.includes(cf))) {
          return false;
        }
        if (!formInfo.keywords.some(kw => normProd.includes(kw))) {
          return false;
        }
      }
    }

    // 3. CANDADO DE MARCA VS PRINCIPIO ACTIVO
    if (qTokens.length > 0) {
      const firstWord = qTokens[0];
      let isActiveIngredient = false;
      
      if (typeof ISP_DATA !== 'undefined' && ISP_DATA.principios_activos) {
        const paKeys = Object.keys(ISP_DATA.principios_activos);
        if (paKeys.some(pa => pa.includes(firstWord) || firstWord.includes(pa))) {
          isActiveIngredient = true;
        }
      }

      // Si no es un principio activo conocido, asumimos que es una MARCA especifica.
      // En ese caso, exigimos que el nombre del producto contenga la marca buscada.
      if (!isActiveIngredient) {
        if (!normProd.includes(firstWord)) {
          return false;
        }
      }
    }

    // 4. MATCH INCLUSIVO (Sin restricciones de listas cerradas)
    return true;
  }
};

if (typeof window !== "undefined") {
  window.ISPEngine = ISPEngineClient;
}
