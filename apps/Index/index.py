from flask import render_template
from flask import Blueprint
from apps.Index.__init__ import index_bp


# index_bp = Blueprint('index', __name__, url_prefix='/index')


@index_bp.route('/', methods=["POST", "GET"], endpoint='user_index')
def user_index():
    return render_template('index/index.html')
