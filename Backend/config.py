from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "clave_por_defecto_solo_desarrollo")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MAIL_EMAIL     = os.getenv("MAIL_EMAIL")
MAIL_PASSWORD  = os.getenv("MAIL_PASSWORD")