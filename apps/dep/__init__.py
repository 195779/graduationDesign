from flask import Blueprint


depAdmin_bp = Blueprint('depAdmin_all', __name__, url_prefix='/depAdmin')


from . import dep_manage