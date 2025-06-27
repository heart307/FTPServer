#!/usr/bin/env python3
"""
开发环境快速启动脚本
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """检查环境要求"""
    print("检查环境要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ Python版本需要3.8或更高")
        return False
    
    # 检查是否在虚拟环境中
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  建议在虚拟环境中运行")
    
    print("✅ Python环境检查通过")
    return True

def install_dependencies():
    """安装依赖"""
    print("安装Python依赖...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ backend目录不存在")
        return False
    
    requirements_file = backend_dir / "requirements.txt"
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, cwd=backend_dir)
        print("✅ Python依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def setup_database():
    """设置数据库"""
    print("设置数据库...")
    
    backend_dir = Path("backend")
    os.chdir(backend_dir)
    
    # 设置环境变量
    os.environ['FLASK_APP'] = 'run.py'
    os.environ['FLASK_ENV'] = 'development'
    
    try:
        # 初始化数据库
        from app import create_app, db
        from app.models import SystemConfig
        
        app = create_app('development')
        with app.app_context():
            db.create_all()
            
            # 初始化系统配置
            SystemConfig.init_default_configs()
            
            print("✅ 数据库初始化完成")
        
        return True
    except Exception as e:
        print(f"❌ 数据库设置失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("启动后端服务...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ backend目录不存在")
        return None
    
    # 设置环境变量
    env = os.environ.copy()
    env.update({
        'FLASK_APP': 'run.py',
        'FLASK_ENV': 'development',
        'DATABASE_URL': 'sqlite:///dev.db',
        'REDIS_URL': 'redis://localhost:6379/0',
        'JWT_SECRET_KEY': 'dev-jwt-secret-key',
    })
    
    try:
        process = subprocess.Popen([
            sys.executable, "run.py"
        ], cwd=backend_dir, env=env)
        
        # 等待服务启动
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ 后端服务启动成功 (http://localhost:5000)")
            return process
        else:
            print("❌ 后端服务启动失败")
            return None
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("启动前端服务...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("⚠️  frontend目录不存在，跳过前端启动")
        return None
    
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("⚠️  package.json不存在，跳过前端启动")
        return None
    
    try:
        # 检查是否安装了依赖
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            print("安装前端依赖...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # 启动开发服务器
        process = subprocess.Popen([
            "npm", "run", "dev"
        ], cwd=frontend_dir)
        
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ 前端服务启动成功 (http://localhost:3000)")
            return process
        else:
            print("❌ 前端服务启动失败")
            return None
    except FileNotFoundError:
        print("⚠️  npm未安装，跳过前端启动")
        return None
    except Exception as e:
        print(f"❌ 启动前端服务失败: {e}")
        return None

def main():
    """主函数"""
    print("🚀 FTP文件传输管理系统 - 开发环境启动")
    print("=" * 50)
    
    # 检查环境
    if not check_requirements():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 设置数据库
    if not setup_database():
        sys.exit(1)
    
    # 启动服务
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)
    
    frontend_process = start_frontend()
    
    print("\n" + "=" * 50)
    print("🎉 服务启动完成!")
    print("📖 API文档: http://localhost:5000/api/docs")
    if frontend_process:
        print("🌐 前端界面: http://localhost:3000")
    print("📊 后端API: http://localhost:5000/api")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务...")
        
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
        
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
