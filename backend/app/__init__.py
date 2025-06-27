from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from celery import Celery
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
socketio = SocketIO()
celery = Celery()

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    from app.config import config
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')
    
    # 配置Celery
    configure_celery(app, celery)
    
    # 注册蓝图
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 注册Socket.IO事件
    from app.core.socketio_events import register_socketio_events
    register_socketio_events(socketio)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

def configure_celery(app, celery):
    """配置Celery"""
    celery.conf.update(
        broker_url=app.config['REDIS_URL'],
        result_backend=app.config['REDIS_URL'],
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        task_routes={
            'app.core.tasks.transfer_file': {'queue': 'transfer'},
            'app.core.tasks.monitor_folder': {'queue': 'monitor'},
            'app.core.tasks.cleanup_tasks': {'queue': 'cleanup'},
        },
        beat_schedule={
            'cleanup-completed-tasks': {
                'task': 'app.core.tasks.cleanup_tasks',
                'schedule': 3600.0,  # 每小时执行一次
            },
            'update-folder-monitors': {
                'task': 'app.core.tasks.update_folder_monitors',
                'schedule': 300.0,  # 每5分钟执行一次
            },
        }
    )
    
    class ContextTask(celery.Task):
        """使Celery任务在Flask应用上下文中运行"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
