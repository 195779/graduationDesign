from flask import Blueprint

staff_bp = Blueprint('staff_manage', __name__, url_prefix='/staff_manage')

from . import staff_manage