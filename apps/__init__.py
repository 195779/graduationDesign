from flask import Flask

from apps.Index.__init__ import index_bp
from apps.Login.__init__ import login_bp
from apps.Staff_Manage.__init__ import staff_bp
from config import DevelopmentConfig
from exts import db


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    # 加载配置
    app.config.from_object(DevelopmentConfig)
    #
    db.init_app(app)
    # 注册蓝图
    app.register_blueprint(login_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(staff_bp)
    return app