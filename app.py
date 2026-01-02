import json
import os
from flask import Flask, request, jsonify
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# ----------------- ENV -----------------
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)

# ----------------- GOOGLE SHEETS -----------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
CREDS = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

client = gspread.authorize(CREDS)
sheet = client.open_by_key(
    "1nVTxaeFv0WMXhD4bxvY70CbH-2hWWcaXGKVbZFA1xKQ"
).sheet1

# ----------------- EMAILS -----------------
def enviar_email(destinatario, nombre):
    msg = EmailMessage()
    msg["Subject"] = "Flowcore recibió tu solicitud ✅"
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario

    msg.set_content(f"""
Hola {nombre},

Recibimos tu solicitud correctamente.
En breve nos pondremos en contacto contigo.

Gracias por escribirnos.

—
Flowcore
Automatización de procesos
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)


def notificar_interno(nombre, servicio, email):
    msg = EmailMessage()
    msg["Subject"] = "Nuevo lead Flowcore 🚀"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER

    msg.set_content(f"""
Nuevo contacto recibido:

Nombre: {nombre}
Servicio: {servicio}
Email: {email}
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

# ----------------- WEBHOOK -----------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    nombre = data.get("nombre", "")
    servicio = data.get("servicio", "")
    email = data.get("email", "")

    sheet.append_row([fecha, nombre, servicio, email])

    if email:
        enviar_email(email, nombre)

    notificar_interno(nombre, servicio, email)

    print("📩 Guardado y email enviado")
    return jsonify({"status": "ok"})

# ----------------- RUN -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
