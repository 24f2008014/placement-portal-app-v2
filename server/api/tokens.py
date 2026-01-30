from flask import Blueprint, current_app, url_for, request, abort
from apifairy import authenticate, body, response, other_responses
from api import db
from api.auth import basic_auth
from api.schemas import TokenSchema, EmptySchema
from api.models import RefreshToken, User
from werkzeug.http import dump_cookie
import jwt
import hashlib, secrets
from datetime import datetime, timedelta, timezone

tokens = Blueprint("tokens", __name__)
token_schema = TokenSchema()
empty_schema = EmptySchema()

def hash_token(token):
    """Returns a sha256 hash digest for a given token."""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_access_token(user_id, roles):
    """Returns a new access token."""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=current_app.config["ACCESS_TOKEN_MINUTES"])
    return jwt.encode(
        payload={
            "sub": str(user_id),
            "exp": expires_at,
            "roles": roles
        },
        key=current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

def generate_refresh_token(user_id):
    """Returns a new refresh token and adds it to the database."""
    expires_at = datetime.now(timezone.utc) + timedelta(days=current_app.config["REFRESH_TOKEN_DAYS"])
    raw = secrets.token_urlsafe()
    hash = hash_token(raw)
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=hash,
        expires_at=expires_at
    )
    db.session.add(refresh_token)
    db.session.commit()
    return raw

def token_response(access_token, refresh_token):
    """Formats the access token + refresh token response."""
    headers = {
        "Set-Cookie": dump_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax", # "strict" for prod. also add `secure=True`.
            path=url_for("tokens.refresh"),
            max_age=int(current_app.config["REFRESH_TOKEN_DAYS"])*24*60*60,
        )
    }
    return {
        "access_token": access_token,
        "expires_in_seconds": int(current_app.config["ACCESS_TOKEN_MINUTES"]) * 60,
    }, 200, headers

@tokens.route("/tokens/new", methods=["POST"])
@authenticate(basic_auth)
@response(token_schema)
@other_responses({401: "Invalid login credentials."})
def get_token():
    """Returns an access token (in the response body) and a refresh token (in an HttpOnly cookie)."""
    user = basic_auth.current_user()
    access_token = generate_access_token(user.id, user.get_roles())
    refresh_token = generate_refresh_token(user.id)

    return token_response(access_token, refresh_token)

@tokens.route("/tokens/refresh", methods=["POST"])
@response(token_schema)
@other_responses({401: "Invalid refresh token."})
def refresh():
    """Refresh an access token, given a valid refresh token passed as a cookie."""
    raw = request.cookies.get("refresh_token")
    if not raw:
        abort(401)
    # old_token = db.session.execute(db.select(RefreshToken).where(RefreshToken.token_hash == hash)).scalar()
    old_token = db.session.scalar(db.select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw)))
    if not old_token.is_valid:
        abort(401)
    user = db.session.get(User, int(old_token.user_id))
    access_token = generate_access_token(user.id, user.get_roles())
    refresh_token = generate_refresh_token(user.id)
    old_token.is_revoked = True
    db.session.commit()

    return token_response(access_token, refresh_token)

# @tokens.route("/tokens/revoke", methods=["POST"])
# @response(EmptySchema, status_code=204, description="Refresh token revoked.")
# @other_responses({401: "Invalid refresh token."})
# def revoke(args):
#     """Revokes an existing refresh token."""
#     raw = request.cookies.get("refresh_token")
#     if not raw:
#         abort(401)
#     # old_token = db.session.execute(db.select(RefreshToken).where(RefreshToken.token_hash == hash)).scalar()
#     old_token = db.session.scalar(db.select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw)))
#     old_token.is_revoked = True
#     db.session.commit()
#     return {}