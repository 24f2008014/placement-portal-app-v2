from api.app import db
from api.models import Application
from celery import shared_task
import csv
import os
from flask import current_app
from uuid import uuid4

@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> int:
    return a + b

@shared_task(ignore_result=False)
def export_applications_csv(student_id):
    applications = db.session.scalars(db.select(Application).filter(Application.student_id == student_id))
    filename = f"{str(uuid4())}.csv"
    file_path = os.path.join(current_app.config["TEMP_FOLDER"], filename)
    with open(file_path, "w", encoding="utf-8") as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(["id", "student_id", "position_id", "role", "company", "status", "interview_date", "created_at"])
        for a in applications:
            writer.writerow([a.id, a.student_id, a.position_id, a.position.role, a.position.company.name, a.status, a.interview_date, a.created_at])
    return filename