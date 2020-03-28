from flask import Blueprint
import db_session
from __all_models import User

blueprint = Blueprint('users_api', __name__, template_folder='templates')
