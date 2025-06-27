#!/usr/bin/env python3
"""
FTP文件传输管理系统启动脚本
"""
import os
from app import create_app, socketio

# 创建Flask应用
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # 开发环境使用SocketIO运行
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('DEBUG', False),
        use_reloader=False  # 避免重复启动调度器
    )
