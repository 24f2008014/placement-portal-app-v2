from flask import current_app
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from api import db
from api.models import User
from werkzeug.exceptions import Unauthorized, Forbidden
import jwt

basic_auth = HTTPBasicAuth(scheme="custom") # Custom is to avoid the default browser login prompt
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
    """Verifies if the given email/password pair is valid."""
    print(f"trying to verify {email} {password}...")
    user = db.session.scalar(db.select(User).where(User.email == email))
    if (user is not None) and (user.deleted_at is None) and (user.check_password(password)):
        return user # Who is then available as basic_auth.current_user()

@basic_auth.error_handler
def basic_auth_error(status=401):
    """Error handler for basic authentication."""
    error = Forbidden() if status == 403 else Unauthorized() # 401 = unauthorized. 403 = forbidden.
    return {
        "code": error.code,
        "message": error.name,
        "description": error.description
    }, error.code # Override the default 200.

@token_auth.get_user_roles
def get_user_roles(user):
    """Returns the roles associated with a given user."""
    return user.get_roles()

def decode_access_token(access_token_jwt):
    """Decodes an access token and returns its payload."""
    return jwt.decode(
        jwt=access_token_jwt,
        key=current_app.config["SECRET_KEY"],
        algorithms=["HS256"]
    )

@token_auth.verify_token
def verify_token(access_token):
    """Verifies an access token and returns the `User` object associated with the token."""
    try:
        payload = decode_access_token(access_token)
    except jwt.PyJWTError:
        return None
    return db.session.get(User, int(payload["sub"]))

@token_auth.error_handler
def token_auth_error(status=401):
    """Error handler for token authentication."""
    error = Forbidden() if status == 403 else Unauthorized()
    return {
        "code": error.code,
        "message": error.name,
        "description": error.description
    }, error.code # Override the default 200.