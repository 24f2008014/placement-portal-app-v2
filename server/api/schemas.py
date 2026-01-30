from api import db, ma
from marshmallow import validate, validates, validates_schema, ValidationError
from api.auth import token_auth
from api.models import User

class EmptySchema(ma.Schema):
    pass

class TokenSchema(ma.Schema):
    access_token = ma.String(required=True)
    refresh_token = ma.String()
    expires_in_seconds = ma.Integer()

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        description = "This schema represents a user."

    id = ma.auto_field(dump_only=True)
    email = ma.auto_field(required=True, validate=validate.Email(error="Invalid email address."))
    password = ma.String(required=True, load_only=True, validate=[validate.Length(min=8, error="Password must be at least {min} characters long.")])
    created_at = ma.auto_field(dump_only=True)
    deleted_at = ma.auto_field()