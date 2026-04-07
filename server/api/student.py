from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import StudentSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, StudentStatsSchema, PlacementSchema, PositionSchema
from api.models import Position, Application, Placement, Company
from datetime import datetime, timezone
from sqlalchemy import func
from api.tasks import export_applications_csv, send_interview_reminder

student = Blueprint("student", __name__)

@student.route("/students/me/reminder", methods=["GET"])
@authenticate(token_auth, role=["student"])
def daily_reminder_manual():
    """Manually trigger the daily interview reminder email"""
    student_id = token_auth.current_user().student.id
    send_interview_reminder.delay(
        id=student_id,
        subject="Reminder: Upcoming Interviews | Placer",
        template="interview_reminder"
    )
    return "Sent!", 200

@student.route("/student/me/applications/export", methods=["GET"])
@authenticate(token_auth, role=["student"])
def export_applications():
    """Export your applications"""
    student = token_auth.current_user().student
    result = export_applications_csv.delay(student.id)
    return { "result_id": result.id }, 200

@student.route("/students/me/stats", methods=["GET"])
@authenticate(token_auth, role=["student"])
@response(StudentStatsSchema())
def get_student_stats_self():
    """Get student dashboard statistics"""
    student = token_auth.current_user().student
    num_applications = db.session.scalar(db.select(func.count()).select_from(Application).filter(Application.student_id == student.id))
    num_placements = db.session.scalar(db.select(func.count()).select_from(Placement).join(Application).filter(Application.student_id == student.id))
    upcoming_interviews = db.session.scalars(
        db.select(Application)
        .filter(
            Application.student_id == student.id,
            Application.status == "shortlisted",
            Application.interview_date > datetime.now()
        )
    )
    pending_placements = db.session.scalars(
        db.select(Placement)
        .join(Application)
        .filter(
            Application.student_id == student.id,
            Placement.status == "pending"
        )
    )

    return {
        "num_applications": num_applications,
        "num_placements": num_placements,
        "upcoming_interviews": upcoming_interviews,
        "pending_placements": pending_placements
    }

@student.route("/students/me", methods=["GET"])
@authenticate(token_auth, role=["student"])
@response(StudentSchema())
def get_student_self():
    """Return student details"""
    return token_auth.current_user().student

@student.route("/students/me", methods=["PUT"])
@authenticate(token_auth, role=["student"])
@body(StudentSchema(load_instance=False), location="form")
@response(StudentSchema())
def update_student_self(data):
    """Update student profile"""
    student = token_auth.current_user().student
    student.update(data)
    db.session.commit()
    return student

@student.route("/students/me/applications", methods=["GET"])
@authenticate(token_auth, role=["student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_applications_self(args):
    """Get your applications"""
    student = token_auth.current_user().student
    query = db.session.query(Application).join(Position).join(Company).filter(Application.student == student)
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={
            "id": "equals",
            "position_id": "equals",
            "position.role": "ilike",
            "position.company.name": "ilike",
            "created_at": "gt",
            "updated_at": "gt",
            "placement_count": "gt",
            "status": "equals"
        },
        allowed_sort={"id", "position_id", "position.role", "position.company.name", "created_at", "updated_at", "placement_count", "interview_date", "status"},
        endpoint="student.get_applications_self"
    )
    return { "pagination": pagination, "data": items }, 200

@student.route("/positions/<int:id>/applications", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(ApplicationSchema(), 201)
def create_application(id):
    """Create application"""
    student = token_auth.current_user().student

    # Blacklisted students cannot make any new applications
    if student.status == "blacklisted":
        abort(403, "Student is blacklisted.")
    position = db.get_or_404(Position, id)

    # Position must be admin-approved, open for applications, and have a deadline in the future
    if position.status == "closed" or position.is_approved == False or datetime.now() > position.deadline:
        abort(403, "Position must be approved by an administrator and open for applications, and the deadline must be in the future.")
    
    # Student must not have an existing in-progress application
    existing_application = db.session.scalar(
        db.select(Application)
        .join(Position)
        .filter(
            Application.student == student,
            Application.position_id == id,
            Application.status != "withdrawn"
        )
    )
    if existing_application is not None:
        abort(403, "Student already has an in-progress application for this position.")
    
    # Student must meet eligibility criteria
    if student.cgpa < position.min_cgpa:
        abort(403, "Minimum CGPA not met.")
    if student.branch.department not in position.departments:
        abort(403, "Student's department is not eligible.")

    application = Application(student=student, position=position)
    db.session.add(application)
    db.session.commit()
    return application

@student.route("/applications/<int:id>/withdraw", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(ApplicationSchema())
def withdraw_application(id):
    """Withdraw application
    Change an application's status to `withdrawn`.
    
    An application can only be withdrawn if it currently has the `pending` status.
    """
    application = db.get_or_404(Application, id)
    if token_auth.current_user().student != application.student:
        abort(403)
    if application.status != "pending":
        abort(403, "Application must be in the `pending` status.")
    application.status = "withdrawn"
    application.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    return application

@student.route("/placements/<int:id>/accept", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(PlacementSchema())
def accept_placement(id):
    """Accept placement offer"""
    placement = db.get_or_404(Placement, id)
    if token_auth.current_user().student != placement.application.student:
        abort(403)
    if placement.status != "pending":
        abort(403, "Placement must be in the `pending` status.")
    placement.status = "accepted"
    db.session.commit()
    return placement

@student.route("/placements/<int:id>/reject", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(PlacementSchema())
def reject_placement(id):
    """Reject placement offer"""
    placement = db.get_or_404(Placement, id)
    if token_auth.current_user().student != placement.student:
        abort(403)
    if placement.status != "pending":
        abort(403, "Placement must be in the `pending` status.")
    placement.status = "rejected"
    db.session.commit()
    return placement

@student.route("/students/me/positions/unapplied", methods=["GET"])
@authenticate(token_auth, role=["student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PositionSchema()))
def get_positions_unapplied(args):
    """Get open, unapplied-for positions"""
    student = token_auth.current_user().student

    query = db.session.query(Position).join(Company).filter(
        Position.is_approved == True,
        Position.status == "open",
        ~Position.applications.any(Application.student_id == student.id)
    )

    items, pagination = paginate_query(
        query=query,
        model=Position,
        args=args,
        allowed_filters={
            "id": "equals",
            "role": "ilike",
            "company.name": "ilike",
            "salary_min": "gt",
            "salary_max": "gt",
            "min_cgpa": "gt",
            "deadline": "gt",
            "created_at": "gt",
            "application_count": "gt"
        },
        allowed_sort={"id", "role", "company.name", "salary_min", "salary_max", "min_cgpa", "deadline", "created_at", "application_count"},
        endpoint="student.get_positions_unapplied"
    )
    return { "pagination": pagination, "data": items }, 200

@student.route("/students/me/placements", methods=["GET"])
@authenticate(token_auth, role=["student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(PlacementSchema()))
def get_student_placements_self(args):
    """Get your placements"""
    student = token_auth.current_user().student
    query = db.session.query(Placement).join(Application).join(Position).join(Company).filter(Application.student_id == student.id)
    items, pagination = paginate_query(
        query=query,
        model=Placement,
        args=args,
        allowed_filters={
            "id": "equals",
            "application_id": "equals",
            "application.position.role": "ilike",
            "application.position.company.name": "ilike",
            "joining_date": "gt",            
            "salary": "gt",
            "status": "equals",
            "created_at": "gt",
        },
        allowed_sort={"id", "application_id", "application.position.role", "application.position.company.name", "joining_date", "salary", "status", "created_at"},    
        endpoint="student.get_student_placements_self"
    )
    return { "pagination": pagination, "data": items }, 200