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

    link = f"http://localhost:5173/reset-password?token={token}"

    cuerpo = f"""
    <h2>PlomerIA — Restablecer contraseña</h2>

    <p>
      Recibimos una solicitud para restablecer tu contraseña.
    </p>

    <p>
      Hacé clic en el siguiente link:
    </p>

    <a href="{link}" style="
        background-color: #1A5CFF;
        color: white;
        padding: 12px 24px;
        text-decoration: none;
        border-radius: 6px;
        display: inline-block;
    ">
        Restablecer contraseña
    </a>

    <p>
      Si no solicitaste esto, ignorá este email.
    </p>
    """

    enviar_email(
        email,
        "PlomerIA — Restablecer contraseña",
        cuerpo
    )
    
def enviar_solicitud_plomero(
    plomero_email:   str,
    plomero_nombre:  str,
    solicitud_id:    int,
    descripcion:     str,
    diagnostico:     str,
    urgencia:        str,
    presupuesto_min: float,
    presupuesto_max: float,
):
    url           = "http://localhost:8000/solicitudes"
    link_aceptar  = f"{url}/{solicitud_id}/aceptar"
    link_rechazar = f"{url}/{solicitud_id}/rechazar"

    cuerpo = f"""
    <h2>PlomerIA — Nueva solicitud de trabajo</h2>
    <p>Hola <b>{plomero_nombre}</b>, tenés una nueva solicitud:</p>
    <table style="border-collapse:collapse; width:100%">
        <tr><td style="padding:8px"><b>Problema:</b></td>
            <td style="padding:8px">{descripcion}</td></tr>
        <tr style="background:#F3F4F6">
            <td style="padding:8px"><b>Diagnóstico:</b></td>
            <td style="padding:8px">{diagnostico}</td></tr>
        <tr><td style="padding:8px"><b>Urgencia:</b></td>
            <td style="padding:8px">{urgencia}</td></tr>
        <tr style="background:#F3F4F6">
            <td style="padding:8px"><b>Presupuesto estimado:</b></td>
            <td style="padding:8px">${presupuesto_min:,.0f} – ${presupuesto_max:,.0f} ARS</td></tr>
    </table>
    <br/>
    <a href="{link_aceptar}" style="
        background:#0D9E7A; color:white; padding:12px 24px;
        text-decoration:none; border-radius:6px; margin-right:10px;
        display:inline-block;">
        ✅ Aceptar trabajo
    </a>
    <a href="{link_rechazar}" style="
        background:#DC2626; color:white; padding:12px 24px;
        text-decoration:none; border-radius:6px;
        display:inline-block;">
        ❌ Rechazar
    </a>
    <p style="color:#6B7280; font-size:12px; margin-top:20px;">
        Si otro plomero acepta antes, la solicitud se cancela automáticamente.
    </p>
    """
    enviar_email(
        plomero_email,
        f"PlomerIA — Nueva solicitud ({urgencia})",
        cuerpo
    )