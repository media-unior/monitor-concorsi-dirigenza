import sys
from pathlib import Path
from cv_selector_core import choose_cv

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output" / "scelta_cv_per_bando.md"

def main():
    if len(sys.argv) < 2:
        print("Uso: python profilo_strategico/scripts/scegli_cv_per_bando.py \"titolo bando\"")
        raise SystemExit(1)

    title = " ".join(sys.argv[1:])
    result = choose_cv(title)

    lines = []
    lines.append("# Scelta CV per bando")
    lines.append("")
    lines.append("## Titolo bando")
    lines.append("")
    lines.append(title)
    lines.append("")
    lines.append("## CV consigliato")
    lines.append("")
    lines.append(f"`{result['cv']}`")
    lines.append("")
    lines.append("## Motivazione")
    lines.append("")
    lines.append(f"Parole chiave intercettate: {result['score']}")
    lines.append("")
    lines.append("## Progetti da evidenziare")
    lines.append("")
    for p in result["projects"]:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("## Gap da coprire nella candidatura")
    lines.append("")
    for g in result["gaps"]:
        lines.append(f"- {g}")
    lines.append("")
    lines.append("## Ranking alternative")
    lines.append("")
    for score, cv, _ in result["ranking"]:
        lines.append(f"- {cv}: score {score}")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report creato: {OUT}")
    print(f"CV consigliato: {result['cv']}")

if __name__ == "__main__":
    main()
