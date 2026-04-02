from api import db, ma
from marshmallow import validate, validates, validates_schema, ValidationError, fields, pre_load, post_load, pre_dump
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from api.auth import token_auth
from api.models import User, Student, Department, Branch, Industry, Company, Position, Application, Placement, Role
from marshmallow_oneofschema import OneOfSchema
from datetime import datetime
from sqlalchemy import func, asc, desc, select, text
import json
from werkzeug.exceptions import BadRequest
from flask import request, url_for, current_app
from werkzeug.utils import secure_filename
import os
from zoneinfo import ZoneInfo

def to_local(dt: datetime):
    utc_dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    localized_dt = utc_dt.astimezone(ZoneInfo("Asia/Kolkata"))
    return localized_dt

def to_utc(dt):
    naive_dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M')
    localized_dt = naive_dt.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    utc_dt = localized_dt.astimezone(ZoneInfo("UTC"))
    # print(f"naive: {naive_dt}, localized: {localized_dt}, utc: {utc_dt}, final: {utc_dt.replace(tzinfo=None).isoformat()}")
    return utc_dt.replace(tzinfo=None) # .isoformat() is a no no

def paginate_query(query, model, args, allowed_filters, allowed_sort, endpoint):
    limit = int(args.get("limit", 10))
    offset = int(args.get("offset", 10))
    sort_by = args.get("sort_by")
    sort_dir = args.get("sort_dir", "asc")
    filters = args.get("filters", {})

    # Filter
    for k, v in filters.items():
        if k not in allowed_filters.keys():
            raise BadRequest("Bad filter.")
        if len(str(v)) > 0:
            if allowed_filters[k] == "gt":
                print(k, v)
                query = query.filter(getattr(model, k) >= v)
            elif allowed_filters[k] == "lt":
                query = query.filter(getattr(model, k) <= v)
            elif allowed_filters[k] == "equals":
                query = query.filter(getattr(model, k) == v)
            elif allowed_filters[k] == "ilike":
                query = query.filter(getattr(model, k).ilike(f"%{v}%"))
            elif allowed_filters[k] == "ilike_relationship":
                rel_name, rel_attr = str.split(k, ".")
                query = query.join(getattr(model, rel_name))
                query = query.filter(
                    getattr(getattr(model, rel_name).mapper.class_, rel_attr).ilike(f"%{v}%")
                )
    
    # Total number of records
    total = int(db.session.scalar(select(func.count()).select_from(query.subquery())))

    # Sort
    if (sort_by) and (sort_by in allowed_sort):
        sort_col = getattr(model, sort_by, None)
        order = asc(sort_col) if sort_dir == "asc" else desc(sort_col)
        query = query.order_by(order)
    
    # Count
    items = query.limit(limit).offset(offset).all()
    count = len(items)

    pagination = {
        "limit": limit,
        "offset": offset,
        "count": count,
        "total": total
    }

    # Navigation
    def make_link(offset_new):
        q_new = request.args.to_dict(flat=True)
        q_new["offset"] = str(offset_new)
        q_new["limit"] = str(limit)
        return url_for(endpoint, _external=False, **q_new)
    
    if offset + count < total:
        pagination["next"] = make_link(offset + count)
    else:
        pagination["next"] = None
    
    if offset > 0:
        offset_old = max(0, offset - limit)
        pagination["prev"] = make_link(offset_old)
    else:
        pagination["prev"] = None
    
    return items, pagination
    
class ListQueryArgsSchema(ma.Schema):
    limit = fields.Integer(load_default=10)
    offset = fields.Integer(load_default=0, validate=validate.Range(min=0))
    sort_by = fields.String(load_default=None)
    sort_dir = fields.String(load_default="asc", validate=validate.OneOf(["asc", "desc"]))
    filters = fields.Dict(load_default={}, keys=fields.String(), values=fields.Raw())

    @pre_load
    def parse_filters(self, data, **kwargs):
        data.data = data.data.copy() # This is ugly as sin, but args is normally an ImmutableMultiDict. This converts it to a mutable one to edit.
        f = data.get("filters")
        if isinstance(f, str) and f:
            try:
                data["filters"] = json.loads(f)
            except Exception:
                data["filters"] = {}
        
        date_fields = ["created_at", "updated_at", "deleted_at", "deadline", "interview_date", "joining_date"]
        for f in date_fields:
            if f in data["filters"] and data["filters"][f]:
                dt = to_utc(data["filters"][f])
                data["filters"][f] = dt
        return data

class PaginationSchema(ma.Schema):
    limit = fields.Integer()
    offset = fields.Integer()
    count = fields.Integer(dump_only=True)
    total = fields.Integer(dump_only=True)
    prev = fields.String(allow_none=True)
    next = fields.String(allow_none=True)

def PaginatedCollection(schema):
    class PaginatedSchema(ma.Schema):
        pagination = fields.Nested(PaginationSchema)
        data = fields.Nested(schema, many=True)
    PaginatedSchema.__name__ = f"Paginated{schema.__class__.__name__}" # Ex. `PaginatedUser`
    return PaginatedSchema

class EmptySchema(ma.Schema):
    pass

class TokenSchema(ma.Schema):
    access_token = ma.String(required=True)
    refresh_token = ma.String()
    expires_in_seconds = ma.Integer()
    username = fields.String()
    roles = fields.List(fields.String())

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        include_fk = True

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        include_fk = True
        include_relationships = True

    id = auto_field(dump_only=True)
    email = ma.auto_field(required=True, validate=validate.Email(error="Invalid email address."))
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6))
    created_at = ma.auto_field(dump_only=True)
    deleted_at = ma.auto_field()
    roles = fields.Nested(RoleSchema, many=True)

    @pre_dump
    def dt_to_local(self, data, **kwargs):
        if data.created_at:
            data.created_at = to_local(data.created_at)
        if data.deleted_at:
            data.deleted_at = to_local(data.deleted_at)
        return data    

class UpdateUserSchema(UserSchema):
    old_password = fields.String(load_only=True, validate=validate.Length(min=6))

    @validates("old_password")
    def validate_old_password(self, value, **kwargs):
        if not token_auth.current_user().check_password(value):
            raise ValidationError("Old password is incorrect.")

class CompanySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        include_fk = True
        load_instance = True
        sqla_session = db.session
    
    id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    industry = fields.Nested("IndustrySchema", only=("name",), dump_only=True)
    user = fields.Nested(UserSchema, only=("email", "created_at"), dump_only=True)
    
    @validates("name")
    def validate_name(self, value, **kwargs):
        user = token_auth.current_user()
        company_name = user.company.name if user else None
        if (company_name != value) and db.session.scalar(db.select(Company).where(Company.name == value)):
            raise ValidationError("A company with that name already exists.")

class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
        load_instance = True
    id = auto_field(dump_only=True)

class BranchSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Branch
        include_fk = True
    id = auto_field(dump_only=True)
    department_id = auto_field(dump_only=True)
    name = auto_field(dump_only=True)

class IndustrySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Industry
        include_fk = True
    id = auto_field(dump_only=True)
    name = auto_field(dump_only=True)

class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        include_fk = True
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    roll_number = auto_field(validate=validate.Length(min=1))
    gender = auto_field(validate=validate.OneOf(["male", "female", "other"]))
    branch = fields.Nested(BranchSchema, only=("name", "department_id",), dump_only=True)
    user = fields.Nested(UserSchema, only=("email", "created_at"), dump_only=True)
    resume = fields.Raw(load_only=True, required=False)

    @validates("roll_number")
    def validate_roll_number(self, value, **kwargs):
        user = token_auth.current_user()
        old_roll_number = user.student.roll_number if user else None
        if (old_roll_number != value) and db.session.scalar(db.select(Student).where(Student.roll_number == value)):
            raise ValidationError("Roll number in use. Please provide a unique roll number.")
    
    @pre_load
    def check_resume(self, data, **kwargs):
        if "resume" in data and data["resume"].filename.rsplit(".", 1)[1].lower() == "pdf":
            user = token_auth.current_user()
            student_id = user.student.id
            filename = f"{student_id}_{secure_filename(data['resume'].filename)}"
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            data["resume"].save(file_path)
            data["resume_url"] = filename
            data.pop("resume", None)
        return data

class ProfileOneOfSchema(OneOfSchema):
    type_field = "type"

    type_schemas = {
        "student": StudentSchema,
        "company": CompanySchema,
    }

    def get_obj_type(self, obj):
        if isinstance(obj, Student):
            return "student"
        elif isinstance(obj, Company):
            return "company"

class RegisterSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    profile = fields.Nested(ProfileOneOfSchema(), required=True)

    @validates("email")
    def validate_email(self, value, **kwargs):
        if db.session.scalar(db.select(User).where(User.email == value)):
            raise ValidationError("Please use another email.")

class PositionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Position
        include_fk = True
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)
    company_id = auto_field(dump_only=True)
    role = auto_field()
    salary_min = auto_field(validate=validate.Range(min=0))
    salary_max = auto_field(validate=validate.Range(min=0))
    min_cgpa = auto_field(validate=validate.Range(min=0, max=10))
    status = auto_field(validate=validate.OneOf(["open", "closed"]))
    company = fields.Nested(CompanySchema, dump_only=True)
    departments = fields.Nested(DepartmentSchema, many=True, dump_only=True)
    department_ids = fields.List(fields.Integer(), load_only=True)

    @validates("deadline")
    def validate_deadline(self, value, **kwargs):
        if value < datetime.now():
            raise ValidationError("Deadline cannot be in the past.")
        
    @pre_load
    def fix_dates(self, data, **kwargs):
        date_fields = ["deadline"]
        for f in date_fields:
            if f in data and data[f]:
                dt = to_utc(data[f])
                data[f] = dt
        return data
    
    @post_load
    def make_instance(self, data, **kwargs):
        dept_ids = data.pop("department_ids", [])
        instance = super().make_instance(data, **kwargs)
        if dept_ids:
            instance.departments = Department.query.filter(Department.id.in_(dept_ids)).all()
        return instance

    @pre_dump
    def dt_to_local(self, data, **kwargs):
        if data.created_at:
            data.created_at = to_local(data.created_at)
        if data.deadline:
            data.deadline = to_local(data.deadline)
        if data.deleted_at:
            data.deleted_at = to_local(data.deleted_at)
        if data.updated_at:
            data.updated_at = to_local(data.updated_at)
        return data
            
class ApplicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Application
        include_fk = True
        load_instance = True
        sqla_session = db.session

    id = auto_field(dump_only=True)
    student_id = auto_field(dump_only=True)
    position_id = auto_field(dump_only=True)
    status = auto_field(validate=validate.OneOf(["pending", "shortlisted", "selected", "rejected", "withdrawn"]))
    student = fields.Nested(StudentSchema, only=("id", "first_name", "last_name", "roll_number", "resume_url"), dump_only=True)
    position = fields.Nested(PositionSchema, only=("id", "role", "company.name", "company.contact_email"), dump_only=True)
    placements = fields.Nested("PlacementSchema", only=("id", "status"), many=True)

    @pre_load
    def fix_dates(self, data, **kwargs):
        date_fields = ["interview_date"]
        for f in date_fields:
            if f in data and data[f]:
                dt = to_utc(data[f])
                data[f] = dt
        return data

    @pre_dump
    def dt_to_local(self, data, **kwargs):
        if data.created_at:
            data.created_at = to_local(data.created_at)
        if data.interview_date:
            data.interview_date = to_local(data.interview_date)
        if data.updated_at:
            data.updated_at = to_local(data.updated_at)
        if data.deleted_at:
            data.deleted_at = to_local(data.deleted_at)
        return data

    @validates("interview_date")
    def validate_interview_date(self, value, **kwargs):
        if value < datetime.now():
            raise ValidationError("Interview date cannot be in the past.")

class PlacementSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Placement
        include_fk = True
    
    id = auto_field(dump_only=True)
    application_id = auto_field(dump_only=True)
    salary = auto_field(validate=validate.Range(min=0))
    status = auto_field(validate=validate.OneOf(["pending", "accepted", "rejected", "withdrawn"]))
    application = fields.Nested(ApplicationSchema, only=("id", "position.role", "position.company.name", "position.company.id", "position.id", "student.first_name", "student.last_name", "student.roll_number", "student.id"), dump_only=True)

    @pre_load
    def fix_dates(self, data, **kwargs):
        date_fields = ["joining_date"]
        for f in date_fields:
            if f in data and data[f]:
                dt = to_utc(data[f])
                data[f] = dt
        return data

    @validates("joining_date")
    def validate_joining_date(self, value, **kwargs):
        if value < datetime.now():
            raise ValidationError("Deadline cannot be in the past.")

    @pre_dump
    def dt_to_local(self, data, **kwargs):
        if data.created_at:
            data.created_at = to_local(data.created_at)
        if data.joining_date:
            data.joining_date = to_local(data.joining_date)
        if data.deleted_at:
            data.deleted_at = to_local(data.deleted_at)
        return data

class AdminStatsSchema(ma.Schema):
    num_students = fields.Integer()
    num_companies = fields.Integer()
    num_companies_pending = fields.Integer()
    companies_pending = fields.Nested(CompanySchema, only=("id", "name",), many=True, dump_only=True)
    num_positions = fields.Integer()
    num_applications = fields.Integer()
    num_placements = fields.Integer()

class StudentStatsSchema(ma.Schema):
    num_applications = fields.Integer()
    upcoming_interviews = fields.Nested(ApplicationSchema, many=True, dump_only=True)

class CompanyStatsSchema(ma.Schema):
    num_positions = fields.Integer()
    num_applications = fields.Integer()
    num_placements = fields.Integer()
    upcoming_interviews = fields.Nested(ApplicationSchema, many=True, dump_only=True)