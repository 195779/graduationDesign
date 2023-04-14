from flask import Blueprint

test_bp = Blueprint('test_all', __name__, url_prefix='/test')

from . import test