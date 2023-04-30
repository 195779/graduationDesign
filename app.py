from flask import render_template, request
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from apps import create_app
from exts import db

app = create_app()
manager = Manager(app)

# 创建数据库的命令
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    print(app.url_map)
    print(app.secret_key)
    # app.run()
    manager.run()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    return render_template('error/404.html'), 404


@app.before_request
def before_request():
    if not app.url_map.bind('').match(request.path):
        return render_template('../templates/error/404.html'), 404


# python app.py  (app.run())
# python app.py runserver -h host -p port (manager.run())


# 绑定命令到script
# exts
# |-- __init__py
#       |
#           db = SQLAlchemy()
#
# def create_app():
#     app = Flask(__name__)
#     db.init_app(app)
#
#
# migrate = Migrate(app=app, db=db)
# manager.add_command('命令名', MigrateCommand)
#

# 使用命令
# python app.py db init --------> 产生一个文件夹 migrations
#                                 此文件夹中存在versions 文件夹
#                                 用来保存各种更改

# python app.py db migrate --------> 在字段更改后，执行此命令产生一个新版py文件
# python app.py db upgrade --------> 让更改生效，执行新的py文件，但是会产生错误，
# 因为py文件中总为createtable而不是alter修改，所以会产生一个新的表
#