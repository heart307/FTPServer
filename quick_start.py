#!/usr/bin/env python3
"""
快速启动FTP服务器的简单脚本
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ftp_server import FTPServer
    
    print("🚀 启动Python FTP服务器")
    print("=" * 40)
    
    # 创建FTP根目录
    root_dir = Path("./ftp_root")
    root_dir.mkdir(exist_ok=True)
    (root_dir / "uploads").mkdir(exist_ok=True)
    (root_dir / "downloads").mkdir(exist_ok=True)
    (root_dir / "public").mkdir(exist_ok=True)
    
    # 创建README文件
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

连接信息:
- 地址: localhost
- 端口: 2121

测试命令:
python ftp_client_test.py --test
python ftp_client_test.py --interactive
""")
    
    # 创建服务器实例
    server = FTPServer(
        host='localhost',
        port=2121,
        root_dir=str(root_dir)
    )
    
    print(f"服务器地址: localhost:2121")
    print(f"FTP根目录: {root_dir.absolute()}")
    print(f"支持用户: admin, user, anonymous")
    print("\n可以使用以下方式连接:")
    print("1. 标准FTP客户端: ftp localhost 2121")
    print("2. FileZilla等图形化客户端")
    print("3. Python测试脚本: python ftp_client_test.py --interactive")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 40)
    
    # 启动服务器
    server.start()
    
except KeyboardInterrupt:
    print("\n正在停止FTP服务器...")
    print("✅ 服务器已停止")
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保 ftp_server.py 文件存在且正确")
except Exception as e:
    print(f"❌ 启动失败: {e}")
