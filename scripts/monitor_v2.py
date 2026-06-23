import re
import datetime
import subprocess
from pathlib import Path
from openpyxl import Workbook
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "output" / "concorsi_dirigenza_UTILI_V2.xlsx"
SEEN = BASE / "data" / "seen_links_v2.txt"

today = datetime.date.today().isoformat()

HEADERS = [
    "data", "fonte", "ente", "classe", "titolo", "link",
    "score", "compatibilita", "priorita_biagio", "valutazione_umanoide", "match", "stato_novita", "azione"
]

KEYWORDS = {
    "dirigente": 40,
    "dirigenziale": 40,
    "elevata qualificazione": 30,
    "area funzionari ed elevata qualificazione": 30,
    "area dei funzionari": 20,
    "area funzionari": 20,
    "funzionario": 15,
    "università": 20,
    "ateneo": 20,
    "comunicazione": 25,
    "relazioni esterne": 25,
    "public engagement": 25,
    "terza missione": 25,
    "trasformazione digitale": 20,
    "digitalizzazione": 20,
    "sistemi informativi": 20,
    "portale": 15,
    "web": 10,
    "governance": 20,
    "performance": 15,
    "pnrr": 10,
    "ricerca": 10,
    "internazionalizzazione": 10
}

EXCLUDE = [
    "docente", "docenti", "professore", "professori", "ricercatore", "ricercatori",
    "scuola secondaria", "ministero dell'istruzione", "graduatoria", "insegnamento",
    "borsa", "borse", "assegno", "assegni", "erasmus", "tutorato", "studenti",
    "dirigente medico", "azienda sanitaria", "polizia locale", "asilo nido",
    "istruttore amministrativo", "istruttore servizi", "collaboratore di amministrazione",
    "ponti", "viadotti", "opere strategiche", "economico-finanziaria",
    "funzionario contabile", "ambiente", "agricolo", "neonatologia",
    "fisica", "laboratorio", "astronomia", "settore scientifico tecnologico",
    "settore scientifico-tecnologico"
]

STRONG_BIAGIO = [
    "università", "ateneo", "comunicazione", "relazioni esterne",
    "public engagement", "terza missione", "sistemi informativi",
    "trasformazione digitale", "digitalizzazione", "portale", "web",
    "ricerca scientifica", "performance", "innovazione"
]

def human_eval(title, classe, compat, priorita):
    t = title.lower()

    if "direzione comunicazione e relazioni esterne" in t:
        return "CANDIDARSI"
    if "comunicazione e media" in t:
        return "CANDIDARSI"
    if "terza missione" in t and ("università" in t or "ateneo" in t):
        return "CANDIDARSI"
    if "dirigente" in t and "università" in t and "sistemi informativi" in t:
        return "STUDIARE_SERIAMENTE"
    if "dirigenziale" in t and ("sistemi informativi" in t or "innovazione" in t):
        return "STUDIARE"
    if priorita == "STRATEGICA" and compat == "ALTA":
        return "STUDIARE"
    if priorita == "BUONA":
        return "SOLO_MONITORARE"
    return "SCARTARE_O_BASSA_PRIORITA"

def human_eval(title, classe, compat, priorita):
    t = title.lower()

    if "direzione comunicazione e relazioni esterne" in t:
        return "CANDIDARSI"
    if "comunicazione e media" in t:
        return "CANDIDARSI"
    if "terza missione" in t and ("università" in t or "ateneo" in t):
        return "CANDIDARSI"
    if "dirigente" in t and "università" in t and "sistemi informativi" in t:
        return "STUDIARE_SERIAMENTE"
    if "dirigenziale" in t and ("sistemi informativi" in t or "innovazione" in t):
        return "STUDIARE"
    if priorita == "STRATEGICA" and compat == "ALTA":
        return "STUDIARE"
    if priorita == "BUONA":
        return "SOLO_MONITORARE"
    return "SCARTARE_O_BASSA_PRIORITA"

def human_eval(title, classe, compat, priorita):
    t = title.lower()

    if "direzione comunicazione e relazioni esterne" in t:
        return "CANDIDARSI"
    if "comunicazione e media" in t:
        return "CANDIDARSI"
    if "terza missione" in t and ("università" in t or "ateneo" in t):
        return "CANDIDARSI"
    if "dirigente" in t and "università" in t and "sistemi informativi" in t:
        return "STUDIARE_SERIAMENTE"
    if "dirigenziale" in t and ("sistemi informativi" in t or "innovazione" in t):
        return "STUDIARE"
    if priorita == "STRATEGICA" and compat == "ALTA":
        return "STUDIARE"
    if priorita == "BUONA":
        return "SOLO_MONITORARE"
    return "SCARTARE_O_BASSA_PRIORITA"

def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def classify_title(title):
    t = title.lower()

    if any(x in t for x in EXCLUDE):
        return None

    hits = [k for k in KEYWORDS if k in t]
    score = sum(KEYWORDS[k] for k in hits)

    if "dirigente" in t or "dirigenziale" in t:
        classe = "DIRIGENTE"
        score += 20
    elif "elevata qualificazione" in t or "area dei funzionari" in t or "area funzionari" in t:
        classe = "EQ_FUNZIONARI"
        score += 15
    elif "funzionario" in t and any(x in t for x in ["amministrativo", "comunicazione", "digitalizzazione", "project management", "infrastrutture digitali"]):
        classe = "FUNZIONARIO_GOVERNANCE"
        score += 15
    elif "funzionario" in t:
        classe = "FUNZIONARIO"
    else:
        classe = "ALTRO"

    strong_hits = [x for x in STRONG_BIAGIO if x in t]

    if score >= 80 and strong_hits:
        compat = "ALTA"
    elif score >= 45:
        compat = "MEDIA"
    elif score >= 15:
        compat = "BASSA"
    else:
        return None

    if compat == "ALTA" and any(x in t for x in ["università", "ateneo", "comunicazione", "relazioni esterne", "terza missione", "sistemi informativi"]):
        priorita = "STRATEGICA"
    elif compat in ["ALTA", "MEDIA"] and strong_hits:
        priorita = "BUONA"
    elif compat in ["ALTA", "MEDIA"]:
        priorita = "DA_VERIFICARE"
    else:
        priorita = "BASSA"

    return classe, score, compat, ", ".join(hits), priorita

INPA_QUERIES = [
    "dirigente",
    "dirigenziale",
    "università dirigente",
    "comunicazione",
    "relazioni esterne",
    "terza missione",
    "public engagement",
    "trasformazione digitale",
    "digitalizzazione",
    "sistemi informativi",
    "funzionario comunicazione",
    "funzionario digitale",
    "funzionario amministrativo gestionale"
]


REPORT = BASE / "output" / "report_concorsi_v2.txt"

def write_report(rows):
    selected = [r for r in rows if r[9] in ["CANDIDARSI", "STUDIARE_SERIAMENTE", "STUDIARE"]]
    lines = []
    lines.append(f"REPORT CONCORSI STRATEGICI - {today}")
    lines.append("=" * 60)
    lines.append("")

    if not selected:
        lines.append("Nessun bando strategico o buono trovato.")
    else:
        for i, r in enumerate(sorted(selected, key=lambda x: x[6], reverse=True), 1):
            lines.append(f"{i}. {r[9]} | {r[8]} | {r[7]} | Score {r[6]} | {r[3]}")
            lines.append(r[4])
            lines.append(r[5])
            lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")




def send_email_report(rows):
    selected = [r for r in rows if r[9] in ["CANDIDARSI", "STUDIARE_SERIAMENTE", "STUDIARE"]]
    log_path = BASE / "logs" / "mail_error.log"

    if not selected:
        log_path.write_text("Nessuna mail: nessun bando da inviare\n", encoding="utf-8")
        return

    subject = f"Monitor concorsi - {len(selected)} bandi strategici - {today}"
    report_path = str(REPORT)

    applescript = f"""
set reportFile to POSIX file "{report_path}"
set reportText to read reportFile as «class utf8»
tell application "Mail"
    set newMessage to make new outgoing message with properties {{subject:"{subject}", content:reportText, visible:false}}
    tell newMessage
        make new to recipient at end of to recipients with properties {{address:"bderisi@unior.it"}}
        send
    end tell
end tell
"""

    result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)

    if result.returncode == 0:
        log_path.write_text("Mail inviata correttamente\n", encoding="utf-8")
    else:
        log_path.write_text((result.stderr or result.stdout or "Errore invio mail non specificato") + "\n", encoding="utf-8")

def scan_inpa():
    rows = []
    seen = set(SEEN.read_text(encoding="utf-8").splitlines()) if SEEN.exists() else set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for query in INPA_QUERIES:
            page.goto("https://www.inpa.gov.it/bandi-e-avvisi/", wait_until="networkidle", timeout=60000)

            try:
                page.locator("#ricerca").fill(query)
                page.locator("button[type='submit']").click()
                page.wait_for_load_state("networkidle", timeout=60000)
                page.wait_for_timeout(1500)
            except Exception:
                pass

            links = page.locator("a").all()

            for a in links:
                title = clean(a.inner_text())
                href = a.get_attribute("href") or ""

                if "dettaglio-bando-avviso" not in href:
                    continue

                link = href if href.startswith("http") else "https://www.inpa.gov.it" + href
                result = classify_title(title)

                if not result:
                    continue

                classe, score, compat, hits, priorita = result
                stato = "NUOVO" if link not in seen else "GIÀ VISTO"

                valutazione = human_eval(title, classe, compat, priorita)

                rows.append([
                    today, f"InPA query: {query}", "", classe, title, link,
                    score, compat, priorita, valutazione, hits, stato,
                    "VALUTARE" if valutazione in ["CANDIDARSI", "STUDIARE_SERIAMENTE", "STUDIARE"] else ""
                ])

        browser.close()

    return rows

rows = scan_inpa()

seen_links = set(SEEN.read_text(encoding="utf-8").splitlines()) if SEEN.exists() else set()
# deduplica per link, tenendo il punteggio più alto
best = {}
for r in rows:
    link = r[5]
    if link not in best or r[6] > best[link][6]:
        best[link] = r
rows = list(best.values())

new_seen = seen_links | {r[5] for r in rows}
SEEN.write_text("\n".join(sorted(new_seen)), encoding="utf-8")

wb = Workbook()
ws = wb.active
ws.title = "concorsi_utili_v2"
ws.append(HEADERS)

for r in sorted(rows, key=lambda x: x[6], reverse=True):
    ws.append(r)

wb.save(OUT)
write_report(rows)

new_relevant = [r for r in rows if r[9] in ["CANDIDARSI", "STUDIARE_SERIAMENTE", "STUDIARE"] and r[11] == "NUOVO"]

if new_relevant:
    subprocess.run([
        "osascript", "-e",
        f'display notification "Trovati {len(new_relevant)} nuovi bandi InPA utili" with title "Concorsi dirigenza"'
    ])

print(f"Righe InPA utili: {len(rows)}")
print(f"Nuovi MEDIO/ALTO: {len(new_relevant)}")
print(f"File: {OUT}")

for r in rows:
    if r[9] in ["CANDIDARSI", "STUDIARE_SERIAMENTE", "STUDIARE", "SOLO_MONITORARE"]:
        print(f"[{r[9]} - {r[8]} - {r[7]} - {r[6]} - {r[11]} - {r[3]}] {r[4]}")
        print(r[5])
