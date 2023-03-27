from flask import Blueprint

index_bp = Blueprint('index', __name__, url_prefix='/index')


from . import index_admin

# 当在init文件中创建蓝图实例并在其他文件中使用该蓝图的时候，需要在init最后引入使用蓝图的那个文件