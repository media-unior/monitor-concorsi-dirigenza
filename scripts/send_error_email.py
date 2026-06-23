import os
import smtplib
import ssl
import datetime
import certifi
from pathlib import Path
from email.message import EmailMessage

BASE = Path(__file__).resolve().parents[1]
ENV = BASE / "config" / "mail.env"
LOG = BASE / "logs" / "error_alert.log"

def load_env_file(path):
    data = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data

env_file = load_env_file(ENV)

smtp_user = os.environ.get("SMTP_USER") or env_file.get("SMTP_USER")
smtp_pass = os.environ.get("SMTP_PASS") or env_file.get("SMTP_PASS")
smtp_to = os.environ.get("SMTP_TO") or env_file.get("SMTP_TO")

if not smtp_user or not smtp_pass or not smtp_to:
    raise RuntimeError("SMTP_USER, SMTP_PASS o SMTP_TO mancanti")

today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

body = f"""ERRORE MONITOR CONCORSI - {today}

Il monitor automatico ha rilevato un errore.

Controllare i log del run GitHub Actions o, in locale:
- logs/monitor.log
- logs/monitor_v2.log
- logs/enrich.log
- logs/mail.log
- logs/launchagent.err.log

Cartella:
{BASE}
"""

msg = EmailMessage()
msg["Subject"] = f"ERRORE monitor concorsi - {today}"
msg["From"] = smtp_user
msg["To"] = smtp_to
msg.set_content(body)

context = ssl.create_default_context(cafile=certifi.where())

with smtplib.SMTP_SSL("smtp.mail.me.com", 465, context=context) as server:
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)

LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("Email errore inviata correttamente\n", encoding="utf-8")
