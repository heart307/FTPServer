#!/usr/bin/env python3
"""
FTP服务器演示脚本
展示如何启动服务器并进行基本操作
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path

def create_demo_files():
    """创建演示文件"""
    print("创建演示文件...")
    
    # 创建一些测试文件
    demo_files = {
        "demo.txt": "这是一个演示文件\n包含一些测试内容\n用于FTP传输测试",
        "config.ini": "[settings]\nhost=localhost\nport=2121\nuser=admin",
        "data.json": '{\n  "name": "FTP Demo",\n  "version": "1.0",\n  "files": ["demo.txt", "config.ini"]\n}'
    }
    
    for filename, content in demo_files.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 创建文件: {filename}")

def start_ftp_server_background():
    """在后台启动FTP服务器"""
    print("在后台启动FTP服务器...")
    
    try:
        # 启动FTP服务器进程
        process = subprocess.Popen([
            sys.executable, "start_ftp_server.py", "start"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务器启动
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ FTP服务器已在后台启动")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ FTP服务器启动失败")
            print(f"输出: {stdout.decode()}")
            print(f"错误: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ 启动FTP服务器失败: {e}")
        return None

def demo_ftp_operations():
    """演示FTP操作"""
    print("\n" + "="*50)
    print("演示FTP操作")
    print("="*50)
    
    import ftplib
    
    try:
        # 连接FTP服务器
        print("1. 连接FTP服务器...")
        ftp = ftplib.FTP()
        ftp.connect('localhost', 2121)
        print("   ✅ 连接成功")
        
        # 登录
        print("2. 用户登录...")
        ftp.login('admin', 'admin123')
        print("   ✅ 登录成功")
        
        # 显示当前目录
        print("3. 显示当前目录...")
        current_dir = ftp.pwd()
        print(f"   当前目录: {current_dir}")
        
        # 列出目录内容
        print("4. 列出目录内容...")
        files = []
        ftp.retrlines('LIST', files.append)
        for file_info in files:
            print(f"   {file_info}")
        
        # 创建演示目录
        print("5. 创建演示目录...")
        try:
            ftp.mkd('demo_folder')
            print("   ✅ 目录创建成功: demo_folder")
        except ftplib.error_perm:
            print("   ⚠️  目录已存在: demo_folder")
        
        # 进入演示目录
        print("6. 进入演示目录...")
        ftp.cwd('demo_folder')
        print(f"   当前目录: {ftp.pwd()}")
        
        # 上传文件
        print("7. 上传演示文件...")
        demo_files = ['demo.txt', 'config.ini', 'data.json']
        
        for filename in demo_files:
            if os.path.exists(filename):
                try:
                    with open(filename, 'rb') as f:
                        ftp.storbinary(f'STOR {filename}', f)
                    print(f"   ✅ 上传成功: {filename}")
                except Exception as e:
                    print(f"   ❌ 上传失败: {filename} - {e}")
        
        # 列出上传后的目录内容
        print("8. 列出上传后的目录内容...")
        files = []
        ftp.retrlines('LIST', files.append)
        for file_info in files:
            print(f"   {file_info}")
        
        # 下载文件
        print("9. 下载文件...")
        download_file = 'downloaded_demo.txt'
        try:
            with open(download_file, 'wb') as f:
                ftp.retrbinary('RETR demo.txt', f.write)
            print(f"   ✅ 下载成功: {download_file}")
            
            # 验证下载内容
            with open(download_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   文件内容预览: {content[:50]}...")
            
        except Exception as e:
            print(f"   ❌ 下载失败: {e}")
        
        # 返回根目录
        print("10. 返回根目录...")
        ftp.cwd('/')
        print(f"    当前目录: {ftp.pwd()}")
        
        # 关闭连接
        print("11. 关闭FTP连接...")
        ftp.quit()
        print("    ✅ 连接已关闭")
        
        print("\n✅ FTP操作演示完成!")
        
    except Exception as e:
        print(f"❌ FTP操作演示失败: {e}")

def cleanup_demo_files():
    """清理演示文件"""
    print("\n清理演示文件...")
    
    demo_files = ['demo.txt', 'config.ini', 'data.json', 'downloaded_demo.txt']
    
    for filename in demo_files:
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"  ✅ 删除文件: {filename}")
        except Exception as e:
            print(f"  ❌ 删除文件失败: {filename} - {e}")

def interactive_demo():
    """交互式演示"""
    print("🚀 Python FTP服务器演示")
    print("="*50)
    
    while True:
        print("\n请选择操作:")
        print("1. 创建演示文件")
        print("2. 启动FTP服务器")
        print("3. 运行FTP操作演示")
        print("4. 启动交互式FTP客户端")
        print("5. 运行自动测试")
        print("6. 查看服务器状态")
        print("7. 清理演示文件")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-7): ").strip()
        
        if choice == '0':
            print("退出演示")
            break
        elif choice == '1':
            create_demo_files()
        elif choice == '2':
            server_process = start_ftp_server_background()
            if server_process:
                input("按Enter键继续...")
        elif choice == '3':
            demo_ftp_operations()
        elif choice == '4':
            print("启动交互式FTP客户端...")
            try:
                subprocess.run([sys.executable, "ftp_client_test.py", "--interactive"])
            except Exception as e:
                print(f"启动失败: {e}")
        elif choice == '5':
            print("运行自动测试...")
            try:
                result = subprocess.run([sys.executable, "ftp_client_test.py", "--test"])
                if result.returncode == 0:
                    print("✅ 测试通过")
                else:
                    print("❌ 测试失败")
            except Exception as e:
                print(f"测试失败: {e}")
        elif choice == '6':
            try:
                subprocess.run([sys.executable, "start_ftp_server.py", "status"])
            except Exception as e:
                print(f"查看状态失败: {e}")
        elif choice == '7':
            cleanup_demo_files()
        else:
            print("无效选择，请重新输入")

def auto_demo():
    """自动演示"""
    print("🚀 Python FTP服务器自动演示")
    print("="*50)
    
    # 1. 创建演示文件
    create_demo_files()
    
    # 2. 启动FTP服务器
    server_process = start_ftp_server_background()
    if not server_process:
        print("❌ 无法启动FTP服务器，演示终止")
        return
    
    try:
        # 3. 等待服务器完全启动
        print("等待FTP服务器完全启动...")
        time.sleep(5)
        
        # 4. 运行FTP操作演示
        demo_ftp_operations()
        
        # 5. 运行自动测试
        print("\n" + "="*50)
        print("运行自动测试")
        print("="*50)
        
        try:
            result = subprocess.run([
                sys.executable, "ftp_client_test.py", "--test"
            ], timeout=30)
            
            if result.returncode == 0:
                print("✅ 自动测试通过")
            else:
                print("❌ 自动测试失败")
        except subprocess.TimeoutExpired:
            print("⚠️  测试超时")
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
        
    finally:
        # 6. 停止FTP服务器
        print("\n停止FTP服务器...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("✅ FTP服务器已停止")
        except:
            try:
                server_process.kill()
                print("✅ FTP服务器已强制停止")
            except:
                print("⚠️  无法停止FTP服务器进程")
        
        # 7. 清理演示文件
        cleanup_demo_files()
    
    print("\n🎉 演示完成!")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FTP服务器演示脚本')
    parser.add_argument('--auto', action='store_true', help='运行自动演示')
    parser.add_argument('--interactive', action='store_true', help='运行交互式演示')
    
    args = parser.parse_args()
    
    if args.auto:
        auto_demo()
    elif args.interactive:
        interactive_demo()
    else:
        print("FTP服务器演示脚本")
        print("使用参数:")
        print("  --auto        运行自动演示")
        print("  --interactive 运行交互式演示")
        print("\n示例:")
        print("  python demo.py --auto")
        print("  python demo.py --interactive")

if __name__ == '__main__':
    main()
