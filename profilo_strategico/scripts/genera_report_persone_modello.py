from pathlib import Path
import csv

BASE = Path(__file__).resolve().parents[1]
CSV = BASE / "data" / "persone_modello.csv"
OUT = BASE / "output" / "report_persone_modello.md"

def main():
    rows = []
    with CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("nome"):
                rows.append(r)

    lines = []
    lines.append("# Report persone modello")
    lines.append("")
    lines.append("Obiettivo: individuare pattern ricorrenti nei profili arrivati a responsabilità, EQ o dirigenza.")
    lines.append("")

    if not rows:
        lines.append("Nessuna persona modello ancora inserita.")
        lines.append("")
        lines.append("Prossima azione: raccogliere almeno 10 profili pubblici.")
    else:
        for i, r in enumerate(rows, 1):
            lines.append(f"## {i}. {r['nome']}")
            lines.append("")
            lines.append(f"- Ruolo attuale: {r['ruolo_attuale']}")
            lines.append(f"- Ente: {r['ente']}")
            lines.append(f"- Area: {r['area']}")
            lines.append(f"- Profilo partenza: {r['profilo_partenza']}")
            lines.append(f"- Titoli: {r['titoli_studio']}")
            lines.append(f"- Esperienze chiave: {r['esperienze_chiave']}")
            lines.append(f"- Competenze chiave: {r['competenze_chiave']}")
            lines.append(f"- Passaggi carriera: {r['passaggi_carriera']}")
            lines.append(f"- Da imitare: {r['elementi_da_imitare']}")
            lines.append(f"- Fonte: {r['fonte']}")
            lines.append(f"- Note: {r['note']}")
            lines.append("")

    lines.append("## Pattern da osservare")
    lines.append("")
    lines.append("- presenza di master/corsi manageriali;")
    lines.append("- incarichi di coordinamento;")
    lines.append("- gestione progetti trasversali;")
    lines.append("- lessico su performance, valore pubblico, stakeholder, innovazione;")
    lines.append("- esperienze in commissioni, gruppi di lavoro, digitalizzazione, comunicazione.")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report creato: {OUT}")

if __name__ == "__main__":
    main()
