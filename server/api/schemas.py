from api import db, ma
from marshmallow import validate, validates, validates_schema, ValidationError, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from api.auth import token_auth
from api.models import User, Student, Department, Branch
from marshmallow_oneofschema import OneOfSchema

class EmptySchema(ma.Schema):
    pass

class TokenSchema(ma.Schema):
    access_token = ma.String(required=True)
    refresh_token = ma.String()
    expires_in_seconds = ma.Integer()
    username = fields.String()

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
        if db.session.scalar(db.select(Student).where(Student.roll_number == value)):
            raise ValidationError("Roll number in use. Please provide a unique roll number.")
    # department_id = auto_field(required=True)
    # branch_id = auto_field(required=True)

class ProfileOneOfSchema(OneOfSchema):
    type_field = "type"

    type_schemas = {
        "student": StudentSchema,
    }

    def get_obj_type(self, obj):
        if isinstance(obj, Student):
            return "student"
        
    # def get_data_type(self, data):
    #     try:
    #         return data[self.type_field]
    #     except Exception:
    #         raise ValidationError(f"Missing field {self.type_field} in profile.")

class RegisterSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
    # role = fields.String(required=True, validate=validate.OneOf(["student", "company"]))
    # profile = fields.Dict(required=True)
    # type = fields.String(required=False)
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