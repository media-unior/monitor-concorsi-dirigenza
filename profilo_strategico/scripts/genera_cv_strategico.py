from pathlib import Path
import re

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output" / "cv_strategico_sintetico.md"
PORTFOLIO = BASE / "portfolio_progetti"

PROJECTS = [
    "01_portale_ateneo_cineca.md",
    "02_redazione_web_comunicazione_multimediale.md",
    "03_alma_laurea_alumni.md",
    "04_uscem_pnrr.md",
    "05_infiniti_mondi_terza_missione.md",
]

def section(text, title):
    pattern = rf"## {re.escape(title)}\n(.*?)(?=\n## |\Z)"
    m = re.search(pattern, text, re.S)
    return m.group(1).strip() if m else ""

def read_project(path):
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].replace("#", "").strip()
    return {
        "title": title,
        "sintesi": section(text, "Sintesi"),
        "ruolo": section(text, "Ruolo svolto"),
        "risultati": section(text, "Risultati"),
        "impatto": section(text, "Impatto"),
        "spendibilita": section(text, "Spendibilità concorsuale"),
    }

def main():
    projects = [read_project(PORTFOLIO / p) for p in PROJECTS if (PORTFOLIO / p).exists()]

    lines = []
    lines.append("# CV strategico sintetico - Biagio De Risi")
    lines.append("")
    lines.append("## Profilo")
    lines.append("")
    lines.append(
        "Funzionario universitario e Capo Ufficio nell'area comunicazione digitale, "
        "specializzato in comunicazione istituzionale, digital governance, portali web, "
        "accessibilità, social media, contenuti multimediali, dati, public engagement e innovazione organizzativa nella PA."
    )
    lines.append("")
    lines.append("Profilo ibrido: comunicazione pubblica + tecnologie digitali + analisi dati + coordinamento operativo + processi amministrativi universitari.")
    lines.append("")
    lines.append("## Posizionamento competitivo")
    lines.append("")
    lines.append("- Comunicazione istituzionale digitale: molto forte.")
    lines.append("- Digital governance e portali: forte.")
    lines.append("- Terza missione/public engagement: promettente, da rafforzare.")
    lines.append("- Dati, orientamento, AlmaLaurea/Alumni: differenziante.")
    lines.append("- Management pubblico: in crescita.")
    lines.append("- Profilo dirigenziale: preparatorio, non ancora pienamente maturo.")
    lines.append("")
    lines.append("## Competenze chiave")
    lines.append("")
    lines.append("- Comunicazione istituzionale digitale")
    lines.append("- Digital governance e portali web")
    lines.append("- Coordinamento redazionale e gestione team")
    lines.append("- Accessibilità digitale e qualità dei contenuti")
    lines.append("- Social media e brand reputation")
    lines.append("- Public engagement e terza missione")
    lines.append("- Dati, orientamento, AlmaLaurea e Alumni")
    lines.append("- Project management e processi PA")
    lines.append("- Trasparenza, privacy, anticorruzione, documenti informatici")
    lines.append("- IA generativa e workflow amministrativi")
    lines.append("")
    lines.append("## Progetti strategici")
    lines.append("")

    for p in projects:
        lines.append(f"### {p['title']}")
        lines.append("")
        lines.append(f"**Sintesi:** {p['sintesi']}")
        lines.append("")
        lines.append(f"**Ruolo:** {p['ruolo']}")
        lines.append("")
        lines.append(f"**Risultati:** {p['risultati']}")
        lines.append("")
        lines.append(f"**Impatto:** {p['impatto']}")
        lines.append("")
        lines.append(f"**Spendibilità:** {p['spendibilita']}")
        lines.append("")

    lines.append("## Formula breve per candidature")
    lines.append("")
    lines.append(
        "Funzionario universitario con esperienza nel coordinamento di processi di comunicazione istituzionale digitale, "
        "reingegnerizzazione di portali, governance dei flussi informativi, accessibilità, public engagement, gestione dati "
        "e innovazione organizzativa nella PA. Profilo orientato a ruoli di responsabilità nell'intersezione tra comunicazione, digitale, dati e governance universitaria."
    )
    lines.append("")
    lines.append("## Gap da rafforzare")
    lines.append("")
    lines.append("- Diritto amministrativo avanzato")
    lines.append("- Pubblico impiego e CCNL")
    lines.append("- Ordinamento universitario")
    lines.append("- Performance, valore pubblico e PIAO")
    lines.append("- Contabilità pubblica base")
    lines.append("- Contratti pubblici e MePA avanzato")
    lines.append("- Responsabilità dirigenziale")
    lines.append("- Inglese professionale B2/C1")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"CV strategico creato: {OUT}")

if __name__ == "__main__":
    main()
