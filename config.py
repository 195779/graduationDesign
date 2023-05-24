import os

DEBUG = True
ENV = 'development'

# 设置数据库链接地址
DB_URI = "mysql+pymysql://root:123456@localhost:3306/flask_project"


class Config:
    DEBUG = False
    TESTING = False
    DATABASE_URI = ''
    # SECRET_KEY = os.urandom
    SECRET_KEY = 'secret_key'
    # 是否追踪数据库修改，一般不开启，会影响性能
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 是否显示底层执行的SQL语句
    SQLALCHEMY_ECHO = True
    # 不需要commit 自动保存, 默认False(防止忘记写commit提交)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'  # 配置时区
    SCHEDULER_API_ENABLED = True  # 添加API


class DevelopmentConfig(Config):
    DEBUG = False
    ENV = 'development'
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = DB_URI


class ProductionConfig(Config):
    DATABASE_URI = ''


class TestingConfig(Config):
    TESTING = True
