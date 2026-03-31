from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses, arguments
from api.auth import token_auth
from api.schemas import StudentSchema, paginate_query, ListQueryArgsSchema, PaginatedCollection, ApplicationSchema, StudentStatsSchema, PlacementSchema
from api.models import Student, Position, Application, Placement
from datetime import datetime, timezone
from sqlalchemy import func
from api.tasks import export_applications_csv

student = Blueprint("student", __name__)

@student.route("/student/me/applications/export", methods=["GET"])
@authenticate(token_auth, role=["student"])
def export_applications():
    """Export your applications in .csv format."""
    student = token_auth.current_user().student
    result = export_applications_csv.delay(student.id)
    return { "result_id": result.id }, 200

@student.route("/students/me/stats", methods=["GET"])
@authenticate(token_auth, role=["student"])
@response(StudentStatsSchema())
def get_student_stats_self():
    """Get student statistics for your dashboard."""
    student = token_auth.current_user().student
    return {
        "num_applications": db.session.scalar(db.select(func.count()).select_from(Student).filter(Student.id == student.id))
    }

@student.route("/students/me", methods=["GET"])
@authenticate(token_auth, role=["student"])
@response(StudentSchema())
def get_student_self():
    """Returns a student's details."""
    return token_auth.current_user().student

@student.route("/students/me", methods=["PUT"])
@authenticate(token_auth, role=["student"])
@body(StudentSchema(load_instance=False), location="form")
@response(StudentSchema())
def update_student_self(data):
    """Update your student profile."""
    student = token_auth.current_user().student
    student.update(data)
    db.session.commit()
    return student

@student.route("/students/me/applications", methods=["GET"])
@authenticate(token_auth, role=["student"])
@arguments(ListQueryArgsSchema())
@response(PaginatedCollection(ApplicationSchema()))
def get_applications_self(args):
    """Get a list of applications you've made."""
    student = token_auth.current_user().student
    query = db.session.query(Application).filter(Application.student == student)
    items, pagination = paginate_query(
        query=query,
        model=Application,
        args=args,
        allowed_filters={
            "id": "equals",
            "position_id": "equals",
            "status": "equals",
        },
        allowed_sort={"id", "position_id", "status", "interview_date"},
        endpoint="student.get_applications_self"
    )
    return { "pagination": pagination, "data": items }, 200

@student.route("/positions/<int:id>/applications", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(ApplicationSchema(), 201)
def create_application(id):
    """Create a new application for an open position."""
    student = token_auth.current_user().student
    position = db.get_or_404(Position, id)
    if position.status == "closed" or position.is_approved == False:
        abort(403)
    existing_application = db.session.scalar(db.select(Application).filter(Application.student == student))
    if existing_application is not None:
        abort(403)
    application = Application(student=student, position=position)
    db.session.add(application)
    db.session.commit()
    return application

@student.route("/applications/<int:id>/withdraw", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(ApplicationSchema())
def withdraw_application(id):
    """Withdraw an application you made."""
    application = db.get_or_404(Application, id)
    if token_auth.current_user().student != application.student:
        abort(403)
    if application.status == "withdrawn" or application.position.status == "closed" or application.placements:
        abort(403)
    application.status = "withdrawn"
    application.deleted_at = datetime.now(timezone.utc)
    db.session.commit()
    return application

@student.route("/placements/<int:id>/accept", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(PlacementSchema())
def accept_placement(id):
    """Accept a pending placement offer."""
    placement = db.get_or_404(Placement, id)
    if token_auth.current_user().student != placement.application.student:
        abort(403)
    if placement.status != "pending":
        abort(403)
    placement.status = "accepted"
    db.session.commit()
    return placement

@student.route("/placements/<int:id>/reject", methods=["POST"])
@authenticate(token_auth, role=["student"])
@response(PlacementSchema())
def reject_placement(id):
    """Reject a pending placement offer."""
    placement = db.get_or_404(Placement, id)
    if token_auth.current_user().student != placement.student:
        abort(403)
    if placement.status != "pending":
        abort(403)
    placement.status = "rejected"
    db.session.commit()
    return placement