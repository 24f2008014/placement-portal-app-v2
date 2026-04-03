import os
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv("./.env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "123")
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    ACCESS_TOKEN_MINUTES = int(os.environ.get("ACCESS_TOKEN_MINUTES", 120))
    REFRESH_TOKEN_DAYS = int(os.environ.get("REFRESH_TOKEN_DAYS", 7))

    UPLOAD_FOLDER = "uploads/resumes"
    TEMP_FOLDER = "temp"
    MAX_FILE_SIZE = 2 * 1024 * 1024 # 2 MB

    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_REDIS_HOST = "localhost"

    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost"
    CELERY_TASK_IGNORE_RESULT = True
    CELERY_TIMEZONE = "Asia/Kolkata"
    CELERY_BEAT_SCHEDULE = {
        "daily-reminders": {
            "task": "api.tasks.daily_reminders",
            "schedule": crontab(hour=8, minute=0) # Runs at 8:00 a.m. (IST) daily
        },
        "monthly-report": {
            "task": "api.tasks.monthly_report",
            "schedule": crontab(hour=0, minute=0, day_of_month=1) # Runs at 12:00 a.m. (IST) on the 1st of every month
        }
    }

    MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    MAIL_PORT = os.environ.get("MAIL_PORT", 1025)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "admin@placer.example.com")

    APIFAIRY_TITLE = "Placement Portal Application"
    APIFAIRY_VERSION = "1.0"