import csv
import os
from api.app import db, mail
from api.models import Application, Position, Student, User, Placement, Role
from celery import shared_task
from flask import current_app, render_template
from uuid import uuid4
from flask_mail import Message
from api.schemas import to_local
from sqlalchemy import func
from datetime import datetime, timedelta

@shared_task(ignore_result=False)
def export_applications_csv(student_id):
    """Return all applications of a student as .CSV"""
    applications = db.session.scalars(db.select(Application).filter(Application.student_id == student_id))
    filename = f"{str(uuid4())}.csv"
    file_path = os.path.join(current_app.config["TEMP_FOLDER"], filename)

    with open(file_path, "w", encoding="utf-8") as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow([
            "id", "student_id", "position_id", "role", "company", "status", "interview_date", "created_at"
        ])
        for a in applications:
            writer.writerow([
                a.id, a.student_id, a.position_id, a.position.role, a.position.company.name, a.status, a.interview_date, a.created_at
            ])
    
    return filename

@shared_task
def send_async_email(to, subject, template, **kwargs):
    """Send an email"""
    with current_app.app_context():
        message = Message(
            subject=subject,
            recipients=[to]
        )
        message.body = render_template(f"{template}.txt", **kwargs)
        message.html = render_template(f"{template}.html", **kwargs)
        mail.send(message)

@shared_task
def send_interview_reminder(id, subject, template, **kwargs):
    """Send an email reminding a student of upcoming interviews, if any"""
    student = db.get_or_404(Student, id)
    name = f"{student.first_name} {student.last_name}"
    email = student.user.email

    applications = db.session.scalars(
        db.select(Application)
        .join(Position)
        .filter(
            Application.student_id == id,
            Application.status == "shortlisted",
            Application.interview_date is not None
        )
    ).all()

    if len(applications) == 0:
        return

    interviews = [
        {
            "company": a.position.company.name,
            "interview_date": to_local(a.interview_date),
            "position": a.position.role,
            "application_date": to_local(a.created_at)
        }
        for a in applications
    ]

    send_async_email.delay(
        to=email,
        subject=subject,
        template=template,
        interviews=interviews,
        name=name,
        kwargs=kwargs
    )

@shared_task
def daily_reminders():
    """Send daily reminders of upcoming interviews to relevant students"""
    students = db.session.scalars(db.select(Student.id).filter(Student.status == "whitelisted"))
    for s in students:
        send_interview_reminder.delay(
            id=s,
            subject="Reminder: Upcoming Interviews | Placer",
            template="interview_reminder"
        )

@shared_task
def monthly_report():
    """Send an email with last month's platform statistics to the admin"""
    admin = db.session.scalars(db.select(User).join(User.roles).filter(Role.name == "admin")).first()
    email = admin.email
    
    end_last_month = datetime.today().replace(day=1) - timedelta(days=1)
    start_last_month = end_last_month.replace(day=1)
    month_name = end_last_month.strftime("%B")

    num_positions = db.session.scalar(
        db.select(func.count())
        .select_from(Position)
        .filter(
            Position.created_at >= start_last_month,
            Position.created_at <= end_last_month
        )
    )
    num_applications = db.session.scalar(
        db.select(func.count())
        .select_from(Application)
        .filter(
            Application.created_at >= start_last_month,
            Application.created_at <= end_last_month
        )
    )
    num_placements = db.session.scalar(
        db.select(func.count())
        .select_from(Placement)
        .filter(
            Placement.created_at >= start_last_month,
            Placement.created_at <= end_last_month
        )
    )

    send_async_email.delay(
        to=email,
        subject="Monthly Admin Report | Placer",
        template="monthly_report",
        month=month_name,
        num_positions=num_positions,
        num_applications=num_applications,
        num_placements=num_placements
    )