from pathlib import Path
import csv
from collections import Counter

BASE = Path(__file__).resolve().parents[1]
CSV = BASE / "data" / "vincitori_monitorati.csv"
OUT = BASE / "output" / "report_vincitori_idonei.md"

def main():
    rows = []
    with CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("concorso"):
                rows.append(r)

    lines = []
    lines.append("# Report vincitori e idonei")
    lines.append("")
    lines.append("Obiettivo: individuare pattern professionali nei profili che vincono o risultano idonei.")
    lines.append("")

    if not rows:
        lines.append("Nessun vincitore/idoneo ancora registrato.")
        lines.append("")
        lines.append("Prossima azione: associare ai bandi strategici una verifica periodica degli esiti.")
    else:
        area_counter = Counter(r.get("area", "") for r in rows if r.get("area"))
        comp_counter = Counter()

        for r in rows:
            comps = r.get("competenze_ricorrenti", "")
            for c in comps.split(";"):
                c = c.strip()
                if c:
                    comp_counter[c] += 1

        lines.append("## Aree più ricorrenti")
        lines.append("")
        for area, n in area_counter.most_common():
            lines.append(f"- {area}: {n}")
        lines.append("")

        lines.append("## Competenze ricorrenti")
        lines.append("")
        for comp, n in comp_counter.most_common():
            lines.append(f"- {comp}: {n}")
        lines.append("")

        lines.append("## Schede")
        lines.append("")
        for i, r in enumerate(rows, 1):
            lines.append(f"### {i}. {r['vincitore_o_idoneo']} - {r['ruolo']}")
            lines.append("")
            lines.append(f"- Ente: {r['ente']}")
            lines.append(f"- Concorso: {r['concorso']}")
            lines.append(f"- Area: {r['area']}")
            lines.append(f"- Profilo pubblico: {r['profilo_pubblico']}")
            lines.append(f"- Titoli rilevati: {r['titoli_rilevati']}")
            lines.append(f"- Esperienze rilevate: {r['esperienze_rilevate']}")
            lines.append(f"- Competenze ricorrenti: {r['competenze_ricorrenti']}")
            lines.append(f"- Cosa imparare: {r['cosa_imparare']}")
            lines.append(f"- Fonte graduatoria: {r['graduatoria_url']}")
            lines.append(f"- Note: {r['note']}")
            lines.append("")

    lines.append("## Uso strategico")
    lines.append("")
    lines.append("Ogni profilo vincente deve aggiornare: gap competenze, piano studio, portfolio e lessico CV.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report creato: {OUT}")

if __name__ == "__main__":
    main()
