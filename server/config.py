import os
from dotenv import load_dotenv

load_dotenv("./.env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "123")
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    ACCESS_TOKEN_MINUTES = int(os.environ.get("ACCESS_TOKEN_MINUTES", 120))
    REFRESH_TOKEN_DAYS = int(os.environ.get("REFRESH_TOKEN_DAYS", 7))

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = os.environ.get("MAIL_PORT", 25)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    APIFAIRY_TITLE = "Placement Portal Application"
    APIFAIRY_VERSION = "1.0"