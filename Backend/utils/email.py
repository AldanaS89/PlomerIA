# utils/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from config import MAIL_EMAIL, MAIL_PASSWORD

load_dotenv()


def enviar_email(destinatario: str, asunto: str, cuerpo_html: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = MAIL_EMAIL
    msg["To"]      = destinatario

    parte_html = MIMEText(cuerpo_html, "html")
    msg.attach(parte_html)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(MAIL_EMAIL, MAIL_PASSWORD)
        server.send_message(msg)

def enviar_reset_password(email: str, token: str):
    # En producción esto apuntaría a la app real
    link = f"http://localhost:8000/auth/reset-password?token={token}"

    cuerpo = f"""
    <h2>PlomerIA — Restablecer contraseña</h2>
    <p>Recibimos una solicitud para restablecer tu contraseña.</p>
    <p>Hacé clic en el siguiente link. Expira en 15 minutos:</p>
    <a href="{link}" style="
        background-color: #1A5CFF;
        color: white;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 6px;
        display: inline-block;
    ">Restablecer contraseña</a>
    <p>Si no solicitaste esto, ignorá este email.</p>
    """
    enviar_email(email, "PlomerIA — Restablecer contraseña", cuerpo)