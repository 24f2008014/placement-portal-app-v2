from flask import Blueprint, abort
from api.app import db
from apifairy import authenticate, body, response, other_responses
# from api.auth import token_auth
# from api.schemas import UserSchema, EmptySchema
from api.models import User

main = Blueprint("main", __name__)
# user_schema = UserSchema()
# empty_schema = EmptySchema()

@main.route("/")
def index():
    return "Hello!"