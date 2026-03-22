from api import db, ma
from marshmallow import validate, validates, validates_schema, ValidationError, fields, pre_load
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from api.auth import token_auth
from api.models import User, Student, Department, Branch, Industry, Company, Position, Application, Placement
from marshmallow_oneofschema import OneOfSchema
from datetime import datetime
from sqlalchemy import func, asc, desc, select
import json
from werkzeug.exceptions import BadRequest
from flask import request, url_for

def paginate_query(query, model, args, allowed_filters, allowed_sort, endpoint):
    limit = int(args.get("limit", 10))
    offset = int(args.get("offset", 10))
    sort_by = args.get("sort_by")
    sort_dir = args.get("sort_dir", "asc")
    filters = args.get("filters", {})

    # Filter
    for k, v in filters.items():
        if k not in allowed_filters:
            raise BadRequest("Bad filter.")
        query = query.filter(getattr(model, k) == v)
    
    # Total number of records
    total = int(db.session.scalar(select(func.count()).select_from(query.subquery())))

    # Sort
    if (sort_by) and (sort_by in allowed_sort):
        sort_col = getattr(model, sort_by)
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
    
    @validates("name")
    def validate_name(self, value, **kwargs):
        company = token_auth.current_user().company
        if (company.name != value) and db.session.scalar(db.select(Company).where(Company.name == value)):
            raise ValidationError("A company with that name already exists.")

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

    @validates("roll_number")
    def validate_roll_number(self, value, **kwargs):
        user = token_auth.current_user()
        old_roll_number = user.student.roll_number if user else None
        if (old_roll_number != value) and db.session.scalar(db.select(Student).where(Student.roll_number == value)):
            raise ValidationError("Roll number in use. Please provide a unique roll number.")

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
        
    # def get_data_type(self, data):
    #     try:
    #         return data[self.type_field]
    #     except Exception:
    #         raise ValidationError(f"Missing field {self.type_field} in profile.")

class RegisterSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    profile = fields.Nested(ProfileOneOfSchema(), required=True)

    @validates("email")
    def validate_email(self, value, **kwargs):
        if db.session.scalar(db.select(User).where(User.email == value)):
            raise ValidationError("Please use another email.")

    # @validates_schema
    # def validate_profile(self, data, **kwargs):
    #     r = data.get("role")
    #     profile = data.get("profile", {})
    #     if r == "student":
    #         # StudentSchema.load("profile")
    #         pass

class DepartmentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Department
    id = auto_field(dump_only=True)
    name = auto_field(dump_only=True)

class BranchSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Branch
    id = auto_field(dump_only=True)
    department_id = auto_field(dump_only=True)
    name = auto_field(dump_only=True)

class IndustrySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Industry
    id = auto_field(dump_only=True)
    name = auto_field(dump_only=True)

class PositionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Position
        include_fk = True

    id = auto_field(dump_only=True)
    company_id = auto_field(dump_only=True)
    role = auto_field()
    salary_min = auto_field(validate=validate.Range(min=0))
    salary_max = auto_field(validate=validate.Range(min=0))
    deadline = auto_field()
    min_cgpa = auto_field(validate=validate.Range(min=0, max=10))
    company = fields.Nested(CompanySchema, dump_only=True)

    @validates("deadline")
    def validate_deadline(self, value, **kwargs):
        # if datetime.strptime(value, "%Y-%m-%dT%H:%M") < datetime.now():
        if value < datetime.now():
            raise ValidationError("Deadline cannot be in the past.")

class ApplicationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Application
        include_fk = True

    id = auto_field(dump_only=True)
    student_id = auto_field(dump_only=True)
    position_id = auto_field(dump_only=True)
    status = auto_field(validate=validate.OneOf(["pending", "shortlisted", "offered", "placed", "rejected"]))
    interview_date = auto_field()
    interview_completed = auto_field()
    interview_feedback = auto_field()
    offer_salary = auto_field()
    offer_joining_date = auto_field()
    offer_accepted = auto_field()