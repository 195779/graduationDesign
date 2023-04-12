from flask import Blueprint


gate_bp = Blueprint('gate_all', __name__, url_prefix='/gate')


from . import gate_staff_attend
