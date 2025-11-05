# setting.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 使用 mysqlclient 驱动的配置格式
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+mysqldb://root:root@localhost/fast')
    # 可选但推荐的配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用事件系统，节省内存
    SQLALCHEMY_ECHO = True  # 开发时显示SQL语句（调试用）
    # SQLALCHEMY_POOL_RECYCLE = 3600  # 1小时回收连接
    # SQLALCHEMY_POOL_PRE_PING = True  # 开启连接预检查
    # 添加以下连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # 在每次使用连接前检查连接是否有效
        "pool_recycle": 3600,   # 每1小时回收连接（防止超时）
        "pool_size": 20,        # 连接池大小
        "max_overflow": 30,     # 最大溢出连接数
    }

    # Redis配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_DB = int(os.getenv('REDIS_DB', 0))  # 默认DB编号

    # 邮件配置
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

    #jwt
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时过期时间