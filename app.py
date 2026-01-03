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

creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
creds_dict = json.loads(creds_json)

CREDS = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

client = gspread.authorize(CREDS)
sheet = client.open_by_key(
    "1nVTxaeFv0WMXhD4bxvY70CbH-2hWWcaXGKVbZFA1xKQ"
).sheet1

# ----------------- EMAILS -----------------
def enviar_email_cliente(destinatario, nombre):
    msg = EmailMessage()
    msg["Subject"] = "Flowcore recibió tu solicitud ✅"
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario

    msg.set_content(f"""
Hola {nombre},

Recibimos tu solicitud correctamente.
En breve nos pondremos en contacto contigo.

— Flowcore
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)


def notificar_interno(nombre, servicio, email):
    msg = EmailMessage()
    msg["Subject"] = "🚨 Nuevo lead Flowcore"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER  # interno

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
    nombre = data.get("nombre", "").strip()
    servicio = data.get("servicio", "Otro").strip()
    email = data.get("email", "").strip()

    # 🔒 Normalizar servicio (exacto a tu dropdown)
    SERVICIOS_VALIDOS = [
        "Automatización",
        "Consultoría",
        "Soporte",
        "Otro"
    ]

    if servicio not in SERVICIOS_VALIDOS:
        servicio = "Otro"

    # Guardar en Sheets
    sheet.append_row([fecha, nombre, servicio, email])

    # Emails
    if email:
        enviar_email_cliente(email, nombre)

    notificar_interno(nombre, servicio, email)

    return jsonify({"status": "ok"})

# ----------------- RUN -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
