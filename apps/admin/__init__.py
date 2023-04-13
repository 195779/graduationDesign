from flask import Blueprint


admin_bp = Blueprint('admin_all', __name__, url_prefix='/admin')


from . import admin_manage
