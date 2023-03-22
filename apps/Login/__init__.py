from flask import Blueprint

login_bp = Blueprint('login', __name__, url_prefix='/login')

from . import login

# 当在init文件中创建蓝图实例并在其他文件中使用该蓝图的时候，需要在init最后引入使用蓝图的那个文件
