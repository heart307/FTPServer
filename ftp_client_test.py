#!/usr/bin/env python3
"""
FTP客户端测试脚本
用于测试FTP服务器的功能
"""

import ftplib
import os
import sys
from pathlib import Path

def test_ftp_server(host='localhost', port=2121, username='admin', password='admin123'):
    """测试FTP服务器功能"""
    
    print(f"连接到FTP服务器: {host}:{port}")
    
    try:
        # 连接FTP服务器
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        
        # 登录
        print(f"登录用户: {username}")
        ftp.login(username, password)
        
        print("✅ 连接和登录成功!")
        
        # 测试基本命令
        print("\n=== 测试基本命令 ===")
        
        # 显示当前目录
        current_dir = ftp.pwd()
        print(f"当前目录: {current_dir}")
        
        # 列出目录内容
        print("\n目录内容:")
        files = []
        ftp.retrlines('LIST', files.append)
        for file_info in files:
            print(f"  {file_info}")
        
        # 创建测试目录
        test_dir = 'test_directory'
        try:
            ftp.mkd(test_dir)
            print(f"✅ 创建目录成功: {test_dir}")
        except ftplib.error_perm as e:
            print(f"⚠️  创建目录失败 (可能已存在): {e}")
        
        # 进入测试目录
        try:
            ftp.cwd(test_dir)
            print(f"✅ 进入目录成功: {test_dir}")
            current_dir = ftp.pwd()
            print(f"当前目录: {current_dir}")
        except ftplib.error_perm as e:
            print(f"❌ 进入目录失败: {e}")
        
        # 返回上级目录
        ftp.cwd('..')
        print("✅ 返回上级目录")
        
        # 测试文件上传
        print("\n=== 测试文件上传 ===")
        test_file = 'test_upload.txt'
        test_content = "这是一个测试文件\n用于测试FTP上传功能\n"
        
        # 创建测试文件
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 上传文件
        try:
            with open(test_file, 'rb') as f:
                ftp.storbinary(f'STOR {test_file}', f)
            print(f"✅ 文件上传成功: {test_file}")
        except Exception as e:
            print(f"❌ 文件上传失败: {e}")
        
        # 测试文件下载
        print("\n=== 测试文件下载 ===")
        download_file = 'downloaded_test.txt'
        
        try:
            with open(download_file, 'wb') as f:
                ftp.retrbinary(f'RETR {test_file}', f.write)
            print(f"✅ 文件下载成功: {download_file}")
            
            # 验证下载的文件内容
            with open(download_file, 'r', encoding='utf-8') as f:
                downloaded_content = f.read()
            
            if downloaded_content == test_content:
                print("✅ 文件内容验证成功")
            else:
                print("❌ 文件内容验证失败")
                
        except Exception as e:
            print(f"❌ 文件下载失败: {e}")
        
        # 再次列出目录内容
        print("\n=== 上传后的目录内容 ===")
        files = []
        ftp.retrlines('LIST', files.append)
        for file_info in files:
            print(f"  {file_info}")
        
        # 测试文件删除
        print("\n=== 测试文件删除 ===")
        try:
            ftp.delete(test_file)
            print(f"✅ 文件删除成功: {test_file}")
        except Exception as e:
            print(f"❌ 文件删除失败: {e}")
        
        # 测试目录删除
        print("\n=== 测试目录删除 ===")
        try:
            ftp.rmd(test_dir)
            print(f"✅ 目录删除成功: {test_dir}")
        except Exception as e:
            print(f"❌ 目录删除失败: {e}")
        
        # 关闭连接
        ftp.quit()
        print("\n✅ 所有测试完成，连接已关闭")
        
        # 清理本地测试文件
        try:
            os.remove(test_file)
            os.remove(download_file)
            print("✅ 本地测试文件已清理")
        except:
            pass
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

def interactive_client(host='localhost', port=2121):
    """交互式FTP客户端"""
    
    print(f"FTP交互式客户端")
    print(f"服务器: {host}:{port}")
    print("输入 'help' 查看可用命令，输入 'quit' 退出")
    
    try:
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        
        # 登录
        username = input("用户名: ").strip()
        password = input("密码: ").strip()
        
        ftp.login(username, password)
        print("✅ 登录成功!")
        
        while True:
            try:
                command = input(f"ftp> ").strip()
                
                if not command:
                    continue
                
                if command.lower() == 'quit':
                    break
                elif command.lower() == 'help':
                    print("可用命令:")
                    print("  pwd          - 显示当前目录")
                    print("  ls           - 列出目录内容")
                    print("  cd <dir>     - 改变目录")
                    print("  mkdir <dir>  - 创建目录")
                    print("  rmdir <dir>  - 删除目录")
                    print("  get <file>   - 下载文件")
                    print("  put <file>   - 上传文件")
                    print("  delete <file>- 删除文件")
                    print("  quit         - 退出")
                elif command.lower() == 'pwd':
                    print(ftp.pwd())
                elif command.lower() == 'ls':
                    ftp.retrlines('LIST')
                elif command.lower().startswith('cd '):
                    dirname = command[3:].strip()
                    ftp.cwd(dirname)
                    print(f"目录已改变到: {ftp.pwd()}")
                elif command.lower().startswith('mkdir '):
                    dirname = command[6:].strip()
                    ftp.mkd(dirname)
                    print(f"目录已创建: {dirname}")
                elif command.lower().startswith('rmdir '):
                    dirname = command[6:].strip()
                    ftp.rmd(dirname)
                    print(f"目录已删除: {dirname}")
                elif command.lower().startswith('get '):
                    filename = command[4:].strip()
                    with open(filename, 'wb') as f:
                        ftp.retrbinary(f'RETR {filename}', f.write)
                    print(f"文件已下载: {filename}")
                elif command.lower().startswith('put '):
                    filename = command[4:].strip()
                    if os.path.exists(filename):
                        with open(filename, 'rb') as f:
                            ftp.storbinary(f'STOR {filename}', f)
                        print(f"文件已上传: {filename}")
                    else:
                        print(f"文件不存在: {filename}")
                elif command.lower().startswith('delete '):
                    filename = command[7:].strip()
                    ftp.delete(filename)
                    print(f"文件已删除: {filename}")
                else:
                    print("未知命令，输入 'help' 查看可用命令")
                    
            except ftplib.error_perm as e:
                print(f"权限错误: {e}")
            except ftplib.error_temp as e:
                print(f"临时错误: {e}")
            except Exception as e:
                print(f"错误: {e}")
        
        ftp.quit()
        print("连接已关闭")
        
    except Exception as e:
        print(f"连接失败: {e}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FTP客户端测试工具')
    parser.add_argument('--host', default='localhost', help='FTP服务器地址')
    parser.add_argument('--port', type=int, default=2121, help='FTP服务器端口')
    parser.add_argument('--test', action='store_true', help='运行自动测试')
    parser.add_argument('--interactive', action='store_true', help='启动交互式客户端')
    parser.add_argument('--username', default='admin', help='用户名')
    parser.add_argument('--password', default='admin123', help='密码')
    
    args = parser.parse_args()
    
    if args.test:
        print("=== 运行FTP服务器自动测试 ===")
        success = test_ftp_server(args.host, args.port, args.username, args.password)
        sys.exit(0 if success else 1)
    elif args.interactive:
        interactive_client(args.host, args.port)
    else:
        print("请指定 --test 或 --interactive 参数")
        print("使用 --help 查看帮助信息")

if __name__ == '__main__':
    main()
