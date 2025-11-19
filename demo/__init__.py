from celery import Celery
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import redis  # 新增导入

db = SQLAlchemy()
redis_client = None  # 新增Redis客户端实例
mail = Mail()  # 新增Mail实例
celery = Celery(__name__)  # 新增：Celery 实例

jwt = JWTManager()

def create_app():
    global app_instance  # 声明使用全局变量
    app = Flask(__name__)
    app_instance = app  # 保存实际应用实例
    # 加载配置
    app.config.from_object('demo.setting.Config')

    # 初始化数据库
    db.init_app(app)

    jwt.init_app(app)  # 在create_app中初始化

    # 初始化Redis (新增部分)
    global redis_client
    redis_client = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        password=app.config['REDIS_PASSWORD'],
        db=app.config['REDIS_DB'],
        decode_responses=True  # 自动解码返回字符串
    )

    # 初始化Flask-Mail (新增部分)
    mail.init_app(app)  # 必须在app.config加载后初始化

    # 初始化 Celery
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # 注册蓝图 蓝图和对应的路由映入的名要相同 如果不同的话需要别名再二次使用
    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    from .routes.celery_routes import bp as celery_bp
    from .routes.redis_routes import redis_demo_bp as redis_bp
    from .routes.email_routes import email_bp
    from .routes.copyright_routes import copyright_bp
    from .routes.dingtalk_routes import dingtalk_bp
    from .routes.ffmpeg_routes import ffmpeg_bp
    from .routes.yolo_routes import yolo_bp
    from .routes.yolo_view_routes import yolo_view_bp
    from .controller.yeepay_controller import yeepay_bp  # 新增支付路由

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(celery_bp)
    app.register_blueprint(redis_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(copyright_bp)
    app.register_blueprint(dingtalk_bp)
    app.register_blueprint(ffmpeg_bp)
    app.register_blueprint(yolo_bp)
    app.register_blueprint(yolo_view_bp)
    app.register_blueprint(yeepay_bp)  # 注册支付路由

    return app

def get_app_instance():
    """获取应用实例"""
    global app_instance
    return app_instance
