#!/usr/bin/env python3
"""
FTP服务器启动脚本
提供简单的配置和启动选项
"""

import os
import sys
import argparse
from pathlib import Path
import json

def create_config_file():
    """创建默认配置文件"""
    config = {
        "server": {
            "host": "localhost",
            "port": 2121,
            "root_directory": "./ftp_root"
        },
        "users": {
            "admin": {
                "password": "admin123",
                "permissions": ["read", "write", "delete"]
            },
            "user": {
                "password": "user123", 
                "permissions": ["read", "write"]
            },
            "anonymous": {
                "password": "",
                "permissions": ["read"]
            }
        },
        "logging": {
            "level": "INFO",
            "file": "ftp_server.log"
        }
    }
    
    config_file = Path("ftp_config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 配置文件已创建: {config_file}")
    return config

def load_config():
    """加载配置文件"""
    config_file = Path("ftp_config.json")
    
    if not config_file.exists():
        print("配置文件不存在，创建默认配置...")
        return create_config_file()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 配置文件已加载: {config_file}")
        return config
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        print("使用默认配置...")
        return create_config_file()

def setup_environment(config):
    """设置环境"""
    # 创建FTP根目录
    root_dir = Path(config["server"]["root_directory"])
    root_dir.mkdir(exist_ok=True)
    
    # 创建一些示例目录和文件
    (root_dir / "uploads").mkdir(exist_ok=True)
    (root_dir / "downloads").mkdir(exist_ok=True)
    (root_dir / "public").mkdir(exist_ok=True)
    
    # 创建示例文件
    readme_file = root_dir / "README.txt"
    if not readme_file.exists():
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write("""欢迎使用Python FTP服务器!

目录说明:
- uploads/   : 上传文件目录
- downloads/ : 下载文件目录  
- public/    : 公共文件目录

支持的用户:
- admin     : 管理员用户 (密码: admin123)
- user      : 普通用户 (密码: user123)
- anonymous : 匿名用户 (无密码)

使用FTP客户端连接:
- 地址: localhost
- 端口: 2121
- 用户名和密码见上述说明

测试命令:
python ftp_client_test.py --test
python ftp_client_test.py --interactive
""")
    
    print(f"✅ FTP环境设置完成")
    print(f"   根目录: {root_dir.absolute()}")

def start_server(config):
    """启动FTP服务器"""
    try:
        # 导入FTP服务器
        from ftp_server import FTPServer
        
        # 创建服务器实例
        server = FTPServer(
            host=config["server"]["host"],
            port=config["server"]["port"],
            root_dir=config["server"]["root_directory"]
        )
        
        # 更新用户配置
        server.users = {
            username: user_config["password"] 
            for username, user_config in config["users"].items()
        }
        
        print("🚀 启动FTP服务器...")
        print(f"   地址: {config['server']['host']}")
        print(f"   端口: {config['server']['port']}")
        print(f"   根目录: {config['server']['root_directory']}")
        print(f"   用户: {list(config['users'].keys())}")
        print("\n按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 启动服务器
        server.start()
        
    except KeyboardInterrupt:
        print("\n正在停止FTP服务器...")
    except ImportError:
        print("❌ 无法导入FTP服务器模块，请确保 ftp_server.py 文件存在")
    except Exception as e:
        print(f"❌ 启动FTP服务器失败: {e}")

def show_status():
    """显示服务器状态"""
    config = load_config()
    
    print("FTP服务器配置信息:")
    print("=" * 30)
    print(f"服务器地址: {config['server']['host']}")
    print(f"服务器端口: {config['server']['port']}")
    print(f"根目录: {config['server']['root_directory']}")
    print(f"日志文件: {config['logging']['file']}")
    
    print("\n用户列表:")
    for username, user_config in config['users'].items():
        permissions = ', '.join(user_config.get('permissions', []))
        if user_config['password']:
            print(f"  {username} (密码: {user_config['password']}) - 权限: {permissions}")
        else:
            print(f"  {username} (无密码) - 权限: {permissions}")
    
    # 检查根目录
    root_dir = Path(config['server']['root_directory'])
    if root_dir.exists():
        print(f"\n根目录内容:")
        for item in root_dir.iterdir():
            if item.is_dir():
                print(f"  📁 {item.name}/")
            else:
                size = item.stat().st_size
                print(f"  📄 {item.name} ({size} bytes)")
    else:
        print(f"\n⚠️  根目录不存在: {root_dir}")

def run_test():
    """运行测试"""
    config = load_config()
    
    print("运行FTP服务器测试...")
    
    try:
        import subprocess
        import sys
        
        # 运行测试脚本
        result = subprocess.run([
            sys.executable, "ftp_client_test.py", 
            "--test",
            "--host", config["server"]["host"],
            "--port", str(config["server"]["port"])
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ 测试脚本不存在: ftp_client_test.py")
        return False
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='FTP服务器管理工具')
    parser.add_argument('action', choices=['start', 'config', 'status', 'test'], 
                       help='操作: start(启动), config(配置), status(状态), test(测试)')
    parser.add_argument('--host', help='服务器地址')
    parser.add_argument('--port', type=int, help='服务器端口')
    parser.add_argument('--root', help='FTP根目录')
    
    args = parser.parse_args()
    
    if args.action == 'config':
        print("创建/更新配置文件...")
        config = create_config_file()
        
        # 应用命令行参数
        if args.host:
            config["server"]["host"] = args.host
        if args.port:
            config["server"]["port"] = args.port
        if args.root:
            config["server"]["root_directory"] = args.root
        
        # 保存更新的配置
        with open("ftp_config.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ 配置已更新")
        
    elif args.action == 'status':
        show_status()
        
    elif args.action == 'test':
        success = run_test()
        sys.exit(0 if success else 1)
        
    elif args.action == 'start':
        config = load_config()
        
        # 应用命令行参数覆盖
        if args.host:
            config["server"]["host"] = args.host
        if args.port:
            config["server"]["port"] = args.port
        if args.root:
            config["server"]["root_directory"] = args.root
        
        setup_environment(config)
        start_server(config)

if __name__ == '__main__':
    main()
