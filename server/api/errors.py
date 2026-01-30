from flask import Blueprint
from werkzeug.exceptions import HTTPException
from api.app import apifairy

errors = Blueprint('errors', __name__)

# Catchall. Unlike `errorhandler`, `app_errorhandler` will apply to *every* request,
# not just ones handled by this blueprint.
@errors.app_errorhandler(HTTPException) # base class for all HTTP exceptions
def http_exception(exception):
    return {
        "code": exception.code,
        "message": exception.name,
        "description": exception.description
    }, exception.code

# apifairy will invoke this whenever a validation error is raised by webargs.
@apifairy.error_handler
def validation_error(code, messages):
    return {
        "code": code,
        "message": "Validation error",
        "description": "One or more errors were found in the data you sent.",
        "messages": messages
    }, code