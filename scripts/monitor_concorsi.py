import csv, json, re, datetime, requests
from bs4 import BeautifulSoup
from pathlib import Path
from openpyxl import Workbook

BASE = Path(__file__).resolve().parents[1]
CONFIG = BASE / "config" / "keywords.json"
ATENEI = BASE / "data" / "atenei.csv"
OUT = BASE / "output" / "concorsi_dirigenza_UTILI.xlsx"
ARCHIVE = BASE / "output" / "concorsi_dirigenza_ARCHIVIO_COMPLETO.xlsx"
SEEN = BASE / "data" / "seen_links.txt"
SEEN = BASE / "data" / "seen_links.txt"

today = datetime.date.today().isoformat()
HEADERS = ["data","fonte","ente","titolo","link","score","compatibilita","match","motivo","azione","stato_novita"]

REQUIRE_ANY = ["concorso","selezione","avviso","bando","procedura","dirigente","dirigenziale","personale tecnico amministrativo","tecnico-amministrativo","funzionario","elevata qualificazione"]

EXCLUDE = ["professore","professori","ricercatore","ricercatori","assegno","assegni","borsa","borse","erasmus","tutorato","studente","studenti","docenza","insegnamento","rtd","art. 24","l.240/2010","abilitazione scientifica","mobilità studentesca","massimario"]

SCORE_RULES = {
    "dirigente":30, "dirigenziale":30, "università":15, "ateneo":15,
    "comunicazione":20, "relazioni esterne":20, "public engagement":20,
    "terza missione":20, "trasformazione digitale":15, "digitalizzazione":15,
    "sistemi informativi":15, "portale":10, "web":10, "governance":10,
    "performance":10, "funzionario":8, "elevata qualificazione":15
}

def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def absurl(base, href):
    if not href:
        return ""
    if href.startswith("http"):
        return href
    root = re.match(r"https?://[^/]+", base).group(0)
    return root + href if href.startswith("/") else base.rstrip("/") + "/" + href.lstrip("/")

def get_soup(url):
    r = requests.get(url, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    return BeautifulSoup(r.text, "lxml")

def score_item(text):
    t = text.lower()
    if not any(k in t for k in REQUIRE_ANY):
        return None
    if any(k in t for k in EXCLUDE):
        return None
    hits = [k for k in SCORE_RULES if k in t]
    score = sum(SCORE_RULES[k] for k in hits)
    if score >= 60:
        comp = "ALTA"
    elif score >= 35:
        comp = "MEDIA"
    elif score >= 15:
        comp = "BASSA"
    else:
        return None
    return score, comp, ", ".join(hits)

def add_row(rows, fonte, ente, titolo, link, motivo):
    result = score_item(titolo + " " + link)
    if result:
        score, comp, hits = result
        stato = "NUOVO" if link not in seen_links else "GIÀ VISTO"
        rows.append([today, fonte, ente, titolo, link, score, comp, hits, motivo, "VALUTARE" if comp in ["ALTA","MEDIA"] else "", stato])

def scan_generic(rows, ente, url):
    soup = get_soup(url)
    for a in soup.find_all("a"):
        titolo = clean(a.get_text(" "))
        link = absurl(url, a.get("href"))
        if len(titolo) >= 12:
            add_row(rows, url, ente, titolo, link, "Possibile bando/procedura")

def scan_gazzetta(rows, url):
    soup = get_soup(url)
    detail_links = []
    for a in soup.find_all("a"):
        href = a.get("href") or ""
        if "caricaDettaglio" in href:
            detail_links.append(absurl(url, href))

    for detail in sorted(set(detail_links)):
        try:
            dsoup = get_soup(detail)
            for a in dsoup.find_all("a"):
                titolo = clean(a.get_text(" "))
                link = absurl(detail, a.get("href"))
                if len(titolo) >= 20:
                    add_row(rows, detail, "Gazzetta Ufficiale Concorsi", titolo, link, "Voce da numero Gazzetta")
        except Exception as e:
            rows.append([today, detail, "Gazzetta Ufficiale Concorsi", f"ERRORE DETTAGLIO: {e}", detail, 0, "ERRORE", "", "Numero non letto", "CONTROLLARE"])

def load_sources():
    with open(ATENEI, newline="", encoding="utf-8") as f:
        return [(r["nome"], r["url"]) for r in csv.DictReader(f)]

seen_links = set(SEEN.read_text(encoding="utf-8").splitlines()) if SEEN.exists() else set()
seen_links = set(SEEN.read_text(encoding="utf-8").splitlines()) if SEEN.exists() else set()
rows = []

for ente, url in load_sources():
    try:
        if "gazzettaufficiale.it/30giorni/concorsi" in url:
            scan_gazzetta(rows, url)
        else:
            scan_generic(rows, ente, url)
    except Exception as e:
        rows.append([today, url, ente, f"ERRORE: {e}", url, 0, "ERRORE", "", "Fonte non letta", "CONTROLLARE"])

seen, unique = set(), []
for row in rows:
    key = row[4]
    if key not in seen:
        seen.add(key)
        unique.append(row)

# Archivio completo
wb_all = Workbook()
ws_all = wb_all.active
ws_all.title = "archivio"
ws_all.append(HEADERS)
for row in sorted(unique, key=lambda x: x[5], reverse=True):
    ws_all.append(row)
wb_all.save(ARCHIVE)

# File utile: solo MEDIA, ALTA, ERRORE
useful = [r for r in unique if r[6] in ["ALTA", "MEDIA", "ERRORE"]]

wb = Workbook()
ws = wb.active
ws.title = "concorsi_utili"
ws.append(HEADERS)
for row in sorted(useful, key=lambda x: x[5], reverse=True):
    ws.append(row)
wb.save(OUT)

new_seen = seen_links | {r[4] for r in unique if r[4]}
SEEN.write_text("\n".join(sorted(new_seen)), encoding="utf-8")

new_seen = seen_links | {r[4] for r in unique if r[4]}
SEEN.write_text("\n".join(sorted(new_seen)), encoding="utf-8")

print(f"Righe archivio completo: {len(unique)}")
print(f"Righe utili: {len(useful)}")
print(f"File: {OUT}")

new_relevant = [r for r in unique if r[6] in ["ALTA", "MEDIA"] and r[10] == "NUOVO"]

if new_relevant:
    import platform
    import subprocess

    if platform.system() == "Darwin":
        title = "Nuovi concorsi dirigenza"
        message = f"Trovati {len(new_relevant)} nuovi bandi utili. Apri concorsi_dirigenza_UTILI.xlsx"
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}"'
        ])

print("Match MEDIO/ALTO:")
for r in unique:
    if r[6] in ["ALTA","MEDIA"]:
        print(f"[{r[6]} - {r[5]} - {r[10]}] {r[2]} - {r[3]}")
        print(r[4])
