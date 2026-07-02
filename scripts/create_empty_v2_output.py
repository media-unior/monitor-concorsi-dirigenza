from pathlib import Path
from openpyxl import Workbook
import sys

reason = sys.argv[1] if len(sys.argv) > 1 else "fallback"

base = Path(__file__).resolve().parents[1]
output = base / "output"
output.mkdir(parents=True, exist_ok=True)

out_file = output / "concorsi_dirigenza_UTILI_V2.xlsx"
report_file = output / "report_concorsi_v2.txt"

headers = [
    "data", "fonte", "ente", "classe", "titolo", "link", "score",
    "compatibilita", "priorita_biagio", "valutazione_umanoide",
    "match", "stato_novita", "azione"
]

wb = Workbook()
ws = wb.active
ws.title = "UTILI_V2"
ws.append(headers)
wb.save(out_file)

report_file.write_text(
    "REPORT CONCORSI V2\n"
    "Nessun dato disponibile nel run corrente.\n"
    f"Motivo: {reason}\n",
    encoding="utf-8"
)

print(f"Output V2 vuoto creato: {out_file}")
print(f"Report V2 vuoto creato: {report_file}")
print(f"Motivo: {reason}")
