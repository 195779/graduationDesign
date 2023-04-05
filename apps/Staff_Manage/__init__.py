from flask import Blueprint

staff_bp = Blueprint('staff_all', __name__, url_prefix='/staff_all')

from . import staff_manage