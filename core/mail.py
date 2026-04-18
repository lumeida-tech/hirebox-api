import logging
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings

logger = logging.getLogger(__name__)


async def send_activation_email(email: str, company_name: str, activation_token: str) -> None:
    activation_url = f"{settings.FRONTEND_URL}/auth/activate?token={activation_token}"

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1D9E75;">Bienvenue sur HireBox !</h2>
        <p>Bonjour <strong>{company_name}</strong>,</p>
        <p>Votre compte a été créé avec succès. Cliquez sur le bouton ci-dessous pour activer votre compte :</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{activation_url}"
               style="background-color: #1D9E75; color: white; padding: 14px 28px;
                      text-decoration: none; border-radius: 6px; font-size: 16px;">
                Activer mon compte
            </a>
        </div>
        <p style="color: #666; font-size: 14px;">
            Ou copiez ce lien dans votre navigateur :<br>
            <a href="{activation_url}">{activation_url}</a>
        </p>
        <p style="color: #666; font-size: 14px;">
            Si vous n'avez pas créé de compte, ignorez cet email.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #999; font-size: 12px;">© 2026 HireBox — Widget Intelligent de Recrutement</p>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = "Activez votre compte HireBox"
    message["From"] = settings.MAIL_FROM
    message["To"] = email
    message.attach(MIMEText(html, "html"))

    logger.info("[MAIL] Envoi vers %s via %s:%s", email, settings.MAIL_SERVER, settings.MAIL_PORT)
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            start_tls=settings.MAIL_STARTTLS,
        )
        logger.info("[MAIL] Email envoyé avec succès à %s", email)
    except Exception as e:
        logger.error("[MAIL] Échec envoi à %s : %s", email, e)
        raise


async def send_application_confirmation_email(
    email: str, prenom: str, nom: str, job_title: str
) -> None:
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1D9E75;">Merci d'avoir postulé !</h2>
        <p>Bonjour <strong>{prenom} {nom}</strong>,</p>
        <p>Nous avons bien reçu votre candidature pour le poste :</p>
        <div style="background-color: #f4faf8; border-left: 4px solid #1D9E75;
                    padding: 14px 20px; margin: 20px 0; border-radius: 4px;">
            <strong style="font-size: 16px; color: #1D9E75;">{job_title}</strong>
        </div>
        <p>Notre équipe va étudier votre dossier avec attention. Vous recevrez une réponse dans les plus brefs délais.</p>
        <p style="color: #666; font-size: 14px;">
            En attendant, n'hésitez pas à explorer d'autres offres disponibles sur HireBox.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #999; font-size: 12px;">© 2026 HireBox — Widget Intelligent de Recrutement</p>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = f"Merci d'avoir postulé à {job_title}"
    message["From"] = settings.MAIL_FROM
    message["To"] = email
    message.attach(MIMEText(html, "html"))

    logger.info("[MAIL] Confirmation candidature → %s", email)
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            start_tls=settings.MAIL_STARTTLS,
        )
        logger.info("[MAIL] Confirmation envoyée à %s", email)
    except Exception as e:
        logger.error("[MAIL] Échec confirmation à %s : %s", email, e)
        raise