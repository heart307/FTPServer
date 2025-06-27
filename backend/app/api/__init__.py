from flask import Blueprint, jsonify

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 健康检查接口
@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': 'FTP Manager API is running',
        'version': '1.0.0'
    })

# 导入所有API模块
from . import auth
# from . import sites
# from . import tasks
# from . import monitors
# from . import logs
# from . import system
