from pathlib import Path
import csv
from collections import defaultdict

BASE = Path(__file__).resolve().parents[1]
GAP = BASE / "data" / "gap_competenze.csv"
OUT = BASE / "output" / "piano_studio_12_mesi.md"

MONTHS = [
    ("Mese 1", ["diritto amministrativo", "pubblico impiego"]),
    ("Mese 2", ["diritto amministrativo", "pubblico impiego"]),
    ("Mese 3", ["governance universitaria", "pubblico impiego"]),
    ("Mese 4", ["management pubblico", "performance"]),
    ("Mese 5", ["digitale", "CAD"]),
    ("Mese 6", ["terza missione", "public engagement"]),
    ("Mese 7", ["contabilità pubblica", "programmazione"]),
    ("Mese 8", ["management pubblico", "responsabilità dirigenziale"]),
    ("Mese 9", ["governance universitaria", "trasparenza"]),
    ("Mese 10", ["digitale", "project management"]),
    ("Mese 11", ["prove concorsuali", "casi pratici"]),
    ("Mese 12", ["simulazione", "revisione profilo"]),
]

def read_gaps():
    rows = []
    with GAP.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

def match_rows(rows, terms):
    found = []
    text_terms = [t.lower() for t in terms]
    for r in rows:
        hay = " ".join([
            r.get("area", ""),
            r.get("competenza", ""),
            r.get("azione", ""),
        ]).lower()
        if any(t in hay for t in text_terms):
            found.append(r)
    return found

def main():
    rows = read_gaps()
    lines = []
    lines.append("# Piano studio 12 mesi")
    lines.append("")
    lines.append("Obiettivo: rafforzare il profilo per EQ, responsabilità organizzative, concorsi universitari e traiettoria dirigenziale.")
    lines.append("")

    for month, terms in MONTHS:
        selected = match_rows(rows, terms)
        lines.append(f"## {month}")
        lines.append("")
        if selected:
            for r in selected:
                lines.append(f"- **{r['area']} / {r['competenza']}**")
                lines.append(f"  - livello attuale: {r['livello_attuale']}")
                lines.append(f"  - target: {r['livello_target']}")
                lines.append(f"  - priorità: {r['priorita']}")
                lines.append(f"  - azione: {r['azione']}")
        else:
            lines.append("- Studio trasversale su prove concorsuali, casi pratici e profilo professionale.")
        lines.append("")
        lines.append("Output del mese:")
        lines.append("- 1 scheda sintetica di studio")
        lines.append("- 1 simulazione risposta concorsuale")
        lines.append("- 1 aggiornamento CV/profilo LinkedIn o portfolio competenze")
        lines.append("")

    lines.append("## Regola operativa")
    lines.append("")
    lines.append("Ogni bando utile trovato dal monitor deve essere usato anche come fonte per aggiornare gap, lessico, materie e profilo target.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Piano creato: {OUT}")

if __name__ == "__main__":
    main()
