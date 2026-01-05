import os
import json
import gspread
import smtplib
from zoneinfo import ZoneInfo
from datetime import datetime
from dotenv import load_dotenv
from email.message import EmailMessage
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2.service_account import Credentials

# ----------------- ENV -------------------------------
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ----------------- APP -------------------------------
app = Flask(__name__)
CORS(app)

# ----------------- GOOGLE SHEETS -----------------------
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

# Si existe la variable de entorno, se usa (Railway)
# Si no existe, se cargan credenciales locales
if creds_json:
    creds_dict = json.loads(creds_json)
else:
    with open("credenciales.json", "r", encoding="utf-8") as f:
        creds_dict = json.load(f)

CREDS = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

client = gspread.authorize(CREDS)
sheet = client.open_by_key(
    "1nVTxaeFv0WMXhD4bxvY70CbH-2hWWcaXGKVbZFA1xKQ"
).sheet1

# ----------------- EMAILS ------------------------------------
# No creo seguir usando esto pero bueno, lo haré todo desde Apps Script
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
    msg["To"] = EMAIL_USER  # correo interno

    msg.set_content(f"""
Nuevo contacto recibido:

Nombre: {nombre}
Servicio: {servicio}
Email: {email}
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

# ----------------- WEBHOOK --------------------------------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Mostrar hora de Colombia
    fecha = datetime.now(
        ZoneInfo("America/Bogota")
    ).strftime("%Y-%m-%d %H:%M:%S")

    nombre = data.get("nombre", "").strip()
    servicio = data.get("servicio", "Otro").strip()
    email = data.get("email", "").strip()

    # Normalizar servicio (a mi dropdown)
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

    # Este bloque lo comento porque ya no quiero enviar emails desde acá
    # Emails
    # if email:
    #     enviar_email_cliente(email, nombre)

    # notificar_interno(nombre, servicio, email)

    return jsonify({"status": "ok"})

# ----------------- LEAD (Landing) ---------------------
@app.route("/lead", methods=["POST"])
def recibir_lead():
    data = request.get_json()

    # Hora Colombia
    fecha = datetime.now(
        ZoneInfo("America/Bogota")
    ).strftime("%Y-%m-%d %H:%M:%S")

    nombre = data.get("nombre", "").strip()
    email = data.get("email", "").strip()
    mensaje = data.get("mensaje", "").strip()

    # Guardamos usando el mismo sistema (Google Sheets)
    sheet.append_row([fecha, nombre, "Landing", email])

    print("Lead recibido desde landing:", data)

    return jsonify({
        "status": "ok",
        "mensaje": "Lead recibido correctamente"
    })

# ----------------- RUN -------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
