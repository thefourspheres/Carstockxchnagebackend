import os
from pathlib import Path
import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("SMTP_FROM", SMTP_USER)

BASE_DIR = Path(__file__).resolve().parent  # employee folder

template_env = Environment(
    loader=FileSystemLoader(BASE_DIR / "templates"),
    autoescape=True
)

async def send_welcome_email(to_email: str, username: str, password: str, name: str):
    template = template_env.get_template("welcome_email.html")
    html_content = template.render(
        username=username,
        password=password,
        name=name
    )

    message = EmailMessage()
    message["From"] = FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = "Welcome to the Organization 🎉"

    message.set_content("Welcome to the organization.")
    message.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASSWORD,
        timeout=15,
    )
