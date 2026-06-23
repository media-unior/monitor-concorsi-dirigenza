import os
import smtplib
import ssl
import certifi
from email.message import EmailMessage

smtp_user = os.environ["SMTP_USER"]
smtp_pass = os.environ["SMTP_PASS"]
smtp_to = os.environ["SMTP_TO"]

msg = EmailMessage()
msg["Subject"] = "TEST GitHub Actions - monitor concorsi"
msg["From"] = smtp_user
msg["To"] = smtp_to
msg.set_content("Test riuscito: GitHub Actions può inviare email via SMTP iCloud.")

context = ssl.create_default_context(cafile=certifi.where())

with smtplib.SMTP_SSL("smtp.mail.me.com", 465, context=context) as server:
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)

print("Email test inviata")
