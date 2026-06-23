import re
from pathlib import Path
from openpyxl import load_workbook
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parents[1]
XLSX = BASE / "output" / "concorsi_dirigenza_UTILI_V2.xlsx"
OUT = BASE / "output" / "report_concorsi_v2_arricchito.txt"

HOME = "Casamarciano / Napoli"

TARGET_EVALS = {"CANDIDARSI", "STUDIARE_SERIAMENTE", "STUDIARE"}

CITY_DISTANCE = {
    "napoli": ("MOLTO_FAVOREVOLE", "area Napoli/Campania"),
    "caserta": ("MOLTO_FAVOREVOLE", "Campania"),
    "salerno": ("FAVOREVOLE", "Campania"),
    "benevento": ("FAVOREVOLE", "Campania"),
    "avellino": ("FAVOREVOLE", "Campania"),
    "roma": ("GESTIBILE", "Roma/Lazio"),
    "bari": ("MEDIA", "Sud, distanza gestibile ma non quotidiana"),
    "trento": ("ALTA_PENALITA", "Nord, trasferimento probabile"),
    "trieste": ("ALTA_PENALITA", "Nord-est, trasferimento probabile"),
    "pavia": ("ALTA_PENALITA", "Nord, trasferimento probabile"),
    "padova": ("ALTA_PENALITA", "Nord-est, trasferimento probabile"),
    "genova": ("ALTA_PENALITA", "Nord-ovest, trasferimento probabile"),
    "bologna": ("ALTA_PENALITA", "Nord, trasferimento probabile"),
    "milano": ("ALTA_PENALITA", "Nord, trasferimento probabile"),
    "torino": ("ALTA_PENALITA", "Nord-ovest, trasferimento probabile"),
    "firenze": ("MEDIA_ALTA", "Centro-nord, trasferimento probabile"),
}

def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def infer_distance(title, detail):
    title_l = title.lower()
    detail_l = detail.lower()

    # Prima il titolo: è molto più affidabile del dettaglio InPA, che può contenere footer/testi nazionali.
    for city, value in CITY_DISTANCE.items():
        if city in title_l:
            return value

    # Poi ricerca mirata nel dettaglio, evitando di farsi ingannare da Roma nei footer/testi istituzionali.
    sede_patterns = [
        "sede di lavoro", "sede", "ente di riferimento", "presso", "università degli studi di",
        "politecnico di", "comune di", "provincia di"
    ]
    for pattern in sede_patterns:
        pos = detail_l.find(pattern)
        if pos != -1:
            window = detail_l[pos:pos+500]
            for city, value in CITY_DISTANCE.items():
                if city in window:
                    return value

    return ("DA_VERIFICARE", "sede non riconosciuta automaticamente")

def prestige(text):
    t = text.lower()
    if "università" in t or "politecnico" in t or "ateneo" in t:
        if any(x in t for x in ["pavia", "trento", "trieste", "padova", "bologna", "milano", "torino", "firenze", "napoli"]):
            return "ALTO - Ateneo/Politecnico rilevante"
        return "MEDIO_ALTO - Ente universitario"
    if any(x in t for x in ["ministero", "presidenza del consiglio", "anvur", "mur", "indire", "invalsi", "cineca"]):
        return "ALTO - Ente nazionale/strategico"
    if "comune" in t or "provincia" in t or "unione" in t:
        return "MEDIO - Ente territoriale"
    return "DA_VERIFICARE"

def why_coherent(title, detail):
    t = (title + " " + detail).lower()
    reasons = []

    if "comunicazione" in t or "relazioni esterne" in t:
        reasons.append("coerente con esperienza in comunicazione istituzionale, web, social e relazioni esterne")
    if "terza missione" in t or "public engagement" in t:
        reasons.append("coerente con public engagement, terza missione e valorizzazione istituzionale")
    if "sistemi informativi" in t or "trasformazione digitale" in t or "digitalizzazione" in t or "innovazione" in t:
        reasons.append("coerente con traiettoria comunicazione digitale / governance dei servizi digitali")
    if "area dei funzionari" in t or "elevata qualificazione" in t:
        reasons.append("coerente come passaggio ponte verso EQ, responsabilità organizzativa e crescita manageriale")
    if "dirigente" in t or "dirigenziale" in t:
        reasons.append("coerente come target alto per studio di profili dirigenziali e requisiti futuri")

    if not reasons:
        reasons.append("coerenza da verificare leggendo bando completo")

    return "; ".join(reasons)

def study_topics(title, detail):
    t = (title + " " + detail).lower()
    topics = {"diritto amministrativo", "pubblico impiego", "procedimento amministrativo", "trasparenza e anticorruzione"}

    if "università" in t or "ateneo" in t or "politecnico" in t:
        topics.update(["ordinamento universitario", "CCNL università", "governance degli atenei"])
    if "comunicazione" in t or "relazioni esterne" in t:
        topics.update(["comunicazione pubblica", "legge 150/2000", "accessibilità digitale", "social media policy PA"])
    if "terza missione" in t or "public engagement" in t:
        topics.update(["terza missione", "public engagement", "valutazione ANVUR", "rapporti con territorio e stakeholder"])
    if "sistemi informativi" in t or "digitalizzazione" in t or "trasformazione digitale" in t or "innovazione" in t:
        topics.update(["CAD", "transizione digitale", "cybersecurity PA", "project management ICT", "servizi digitali"])
    if "dirigente" in t or "dirigenziale" in t:
        topics.update(["management pubblico", "performance", "valore pubblico", "responsabilità dirigenziale", "contabilità pubblica base"])

    return ", ".join(sorted(topics))

def final_priority(eval_label, distance_label, prestige_label):
    score = 0

    if eval_label == "CANDIDARSI":
        score += 50
    elif eval_label == "STUDIARE_SERIAMENTE":
        score += 40
    elif eval_label == "STUDIARE":
        score += 30

    if distance_label in ["MOLTO_FAVOREVOLE", "FAVOREVOLE"]:
        score += 20
    elif distance_label == "GESTIBILE":
        score += 10
    elif distance_label == "MEDIA":
        score += 5
    elif distance_label in ["ALTA_PENALITA", "MEDIA_ALTA"]:
        score -= 10

    if prestige_label.startswith("ALTO"):
        score += 20
    elif prestige_label.startswith("MEDIO_ALTO"):
        score += 12
    elif prestige_label.startswith("MEDIO"):
        score += 5

    if score >= 75:
        return "PRIORITA_MASSIMA"
    if score >= 55:
        return "PRIORITA_ALTA"
    if score >= 35:
        return "PRIORITA_MEDIA"
    return "PRIORITA_BASSA"

def load_selected_rows():
    wb = load_workbook(XLSX)
    ws = wb.active
    headers = [c.value for c in ws[1]]
    idx = {h: i for i, h in enumerate(headers)}

    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        data = {h: row[i] for h, i in idx.items()}
        if data.get("valutazione_umanoide") in TARGET_EVALS:
            rows.append(data)
    return rows

def main():
    rows = load_selected_rows()
    lines = []
    lines.append("REPORT CONCORSI ARRICCHITO")
    lines.append(f"Base logistica: {HOME}")
    lines.append("=" * 70)
    lines.append("")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for n, r in enumerate(rows, 1):
            title = clean(r.get("titolo"))
            link = r.get("link")
            eval_label = r.get("valutazione_umanoide")
            classe = r.get("classe")
            score = r.get("score")

            detail = ""
            try:
                page.goto(link, wait_until="networkidle", timeout=60000)
                detail = clean(page.locator("body").inner_text())[:7000]
            except Exception as e:
                detail = f"ERRORE LETTURA DETTAGLIO: {e}"

            dist_label, dist_note = infer_distance(title, detail)
            prestige_label = prestige(title + " " + detail)
            why = why_coherent(title, detail)
            study = study_topics(title, detail)
            priority = final_priority(eval_label, dist_label, prestige_label)

            lines.append(f"{n}. {priority} | {eval_label} | {classe} | Score {score}")
            lines.append(title)
            lines.append("")
            lines.append(f"Perché coerente: {why}")
            lines.append(f"Cosa studiare: {study}")
            lines.append(f"Prestigio: {prestige_label}")
            lines.append(f"Distanza/logistica da {HOME}: {dist_label} - {dist_note}")
            lines.append(f"Link: {link}")
            lines.append("-" * 70)
            lines.append("")

        browser.close()

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report arricchito creato: {OUT}")

if __name__ == "__main__":
    main()
