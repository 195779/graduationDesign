from flask import Flask

from flask import current_app

from apps.Index.__init__ import index_bp
from apps.Login.__init__ import login_bp
from apps.admin.__init__ import admin_bp
from apps.dep.__init__ import depAdmin_bp
from apps.staff.__init__ import staff_bp
from apps.gate.__init__ import gate_bp
from apps.test.__init__ import test_bp
from config import DevelopmentConfig


from exts import db


def create_app(scheduler):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    # 加载配置
    app.config.from_object(DevelopmentConfig)
    #
    db.init_app(app)
    # 注册蓝图
    app.register_blueprint(login_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(gate_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(depAdmin_bp)
    scheduler.init_app(app)
    scheduler.start()
    return app


