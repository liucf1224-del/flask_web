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

    # 测试Redis连接
    try:
        redis_client.ping()
        print("✅ Redis连接成功")
    except redis.ConnectionError:
        print("❌ Redis连接失败")

    # 导入模型（确保在db初始化后导入）
    # from . import models
    # 导入视图
    # from . import views

    # 注册蓝图（如果有）
    # from .views import bp
    # app.register_blueprint(bp)

    # 注册蓝图
    from .controller.ollama_controller import ollama_bp
    app.register_blueprint(ollama_bp)

    # 已有蓝图注册保持不变
    from .routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    from .routes.redis_routes import redis_demo_bp
    app.register_blueprint(redis_demo_bp)
    from .routes.email_routes import email_bp
    app.register_blueprint(email_bp)
    from .routes.copyright_routes import copyright_bp
    app.register_blueprint(copyright_bp)
    from .routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)
    from .routes.celery_routes import bp
    app.register_blueprint(bp)
    from .routes.ffmpeg_routes import ffmpeg_bp
    app.register_blueprint(ffmpeg_bp)
    # 注册YOLO路由
    from .routes.yolo_routes import yolo_bp
    app.register_blueprint(yolo_bp)
    from .routes.yolo_view_routes import yolo_view_bp
    app.register_blueprint(yolo_view_bp)

    return app

def get_app_instance():
    """获取实际应用实例"""
    return app_instance


