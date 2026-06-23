import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output" / "scelta_cv_per_bando.md"

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

def score_title(title, keywords):
    t = title.lower()
    return sum(1 for k in keywords if k in t)

def choose(title):
    results = []
    for cv, data in RULES.items():
        score = score_title(title, data["keywords"])
        results.append((score, cv, data))
    results.sort(reverse=True, key=lambda x: x[0])
    return results

def main():
    if len(sys.argv) < 2:
        print("Uso: python profilo_strategico/scripts/scegli_cv_per_bando.py \"titolo bando\"")
        raise SystemExit(1)

    title = " ".join(sys.argv[1:])
    results = choose(title)
    best_score, best_cv, best_data = results[0]

    lines = []
    lines.append("# Scelta CV per bando")
    lines.append("")
    lines.append(f"## Titolo bando")
    lines.append("")
    lines.append(title)
    lines.append("")
    lines.append("## CV consigliato")
    lines.append("")
    if best_score == 0:
        lines.append("Nessun CV target chiaramente dominante. Usare CV strategico sintetico e valutare manualmente.")
    else:
        lines.append(f"`{best_cv}`")
    lines.append("")
    lines.append("## Motivazione")
    lines.append("")
    lines.append(f"Parole chiave intercettate: {best_score}")
    lines.append("")
    lines.append("## Progetti da evidenziare")
    lines.append("")
    for p in best_data["projects"]:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## Gap da coprire nella candidatura")
    lines.append("")
    for g in best_data["gaps"]:
        lines.append(f"- {g}")
    lines.append("")
    lines.append("## Ranking alternative")
    lines.append("")
    for score, cv, _ in results:
        lines.append(f"- {cv}: score {score}")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report creato: {OUT}")
    print(f"CV consigliato: {best_cv if best_score else 'CV strategico sintetico / valutazione manuale'}")

if __name__ == "__main__":
    main()
