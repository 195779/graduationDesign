from flask import Blueprint

staff_bp = Blueprint('staff_all', __name__, url_prefix='/staff')

from . import staff_get_faces
from . import staff_profile