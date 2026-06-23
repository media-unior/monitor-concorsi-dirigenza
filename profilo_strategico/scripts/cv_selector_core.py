RULES = {
    "cv_eq_comunicazione.md": {
        "keywords": [
            "comunicazione", "media", "relazioni esterne", "redazione",
            "web", "social", "multimediale", "ufficio stampa", "contenuti"
        ],
        "projects": [
            "Redazione Web e Comunicazione Multimediale",
            "Portale di Ateneo / CINECA",
            "Eventi di alta rappresentanza",
            "Infiniti Mondi / Terza Missione"
        ],
        "gaps": [
            "metriche risultati comunicativi",
            "performance e valore pubblico",
            "relazioni esterne e stakeholder"
        ]
    },
    "cv_eq_digital_governance.md": {
        "keywords": [
            "digitale", "digitalizzazione", "sistemi informativi", "innovazione",
            "portale", "cms", "intranet", "accessibilità", "cad",
            "dati", "servizi digitali", "transizione digitale"
        ],
        "projects": [
            "Portale di Ateneo / CINECA",
            "AlmaLaurea / Alumni",
            "Redazione Web e Comunicazione Multimediale",
            "IA e workflow amministrativi"
        ],
        "gaps": [
            "CAD",
            "servizi digitali PA",
            "interoperabilità",
            "qualità dati"
        ]
    },
    "cv_terza_missione_public_engagement.md": {
        "keywords": [
            "terza missione", "public engagement", "territorio",
            "stakeholder", "orientamento", "alumni", "placement",
            "ricerca scientifica", "innovazione territoriale"
        ],
        "projects": [
            "Infiniti Mondi / Terza Missione e Innovazione",
            "USCEM / PNRR",
            "AlmaLaurea / Alumni",
            "Redazione Web e Comunicazione Multimediale"
        ],
        "gaps": [
            "ANVUR",
            "valutazione terza missione",
            "impatto sociale",
            "stakeholder engagement"
        ]
    }
}

def choose_cv(title):
    title_l = str(title or "").lower()
    results = []

    for cv, data in RULES.items():
        score = sum(1 for k in data["keywords"] if k in title_l)
        results.append((score, cv, data))

    results.sort(reverse=True, key=lambda x: x[0])
    best_score, best_cv, best_data = results[0]

    if best_score == 0:
        return {
            "cv": "cv_strategico_sintetico.md",
            "score": 0,
            "projects": ["Valutazione manuale"],
            "gaps": ["Valutazione manuale"],
            "ranking": results,
        }

    return {
        "cv": best_cv,
        "score": best_score,
        "projects": best_data["projects"],
        "gaps": best_data["gaps"],
        "ranking": results,
    }
