import csv
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
FOLLOWUP = BASE / "data" / "bandi_followup.csv"
OUT = BASE / "output" / "report_followup_due.md"

ACTIVE_STATUSES = {"DA_MONITORARE", "DA_CONTROLLARE", ""}

def parse_date(value):
    value = (value or "").strip()
    if not value or value == "DA_VERIFICARE":
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None

def read_rows():
    if not FOLLOWUP.exists():
        raise FileNotFoundError(f"File non trovato: {FOLLOWUP}")

    with FOLLOWUP.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def main():
    today = datetime.now().date()
    rows = read_rows()

    due = []
    future = []
    unknown = []

    for r in rows:
        status = (r.get("stato_followup") or "").strip()
        if status not in ACTIVE_STATUSES:
            continue

        check_date = parse_date(r.get("data_primo_controllo"))

        if check_date is None:
            unknown.append(r)
        elif check_date <= today:
            due.append(r)
        else:
            future.append(r)

    due.sort(key=lambda r: r.get("data_primo_controllo") or "")
    future.sort(key=lambda r: r.get("data_primo_controllo") or "")

    lines = []
    lines.append("# Follow-up bandi da controllare")
    lines.append("")
    lines.append(f"Data report: {today.isoformat()}")
    lines.append("")
    lines.append(f"Da controllare ora: {len(due)}")
    lines.append(f"Controlli futuri: {len(future)}")
    lines.append(f"Data controllo non verificabile: {len(unknown)}")
    lines.append("")

    if due:
        lines.append("## Da controllare ora")
        lines.append("")
        for i, r in enumerate(due, 1):
            lines.append(f"### {i}. {r.get('titolo')}")
            lines.append("")
            lines.append(f"- Ente: {r.get('ente')}")
            lines.append(f"- Sede: {r.get('sede')}")
            lines.append(f"- Scadenza: {r.get('scadenza')}")
            lines.append(f"- Primo controllo esito: {r.get('data_primo_controllo')}")
            lines.append(f"- Valutazione: {r.get('valutazione')}")
            lines.append(f"- Priorità: {r.get('priorita')}")
            lines.append(f"- CV: {r.get('cv_consigliato')}")
            lines.append(f"- Link bando: {r.get('link')}")
            lines.append("")
            lines.append("Azione: cercare approvazione atti, graduatoria, esito, vincitori/idonei e profili pubblici pertinenti.")
            lines.append("")

    lines.append("## Prossimi controlli")
    lines.append("")
    for i, r in enumerate(future[:20], 1):
        lines.append(f"{i}. {r.get('data_primo_controllo')} - {r.get('ente')} - {r.get('titolo')[:120]}")

    if unknown:
        lines.append("")
        lines.append("## Da verificare manualmente")
        lines.append("")
        for i, r in enumerate(unknown, 1):
            lines.append(f"{i}. {r.get('ente')} - {r.get('titolo')[:120]}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Da controllare ora: {len(due)}")
    print(f"Controlli futuri: {len(future)}")
    print(f"Report creato: {OUT}")

if __name__ == "__main__":
    main()
