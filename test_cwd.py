#!/usr/bin/env python3
"""
测试CWD命令的简单FTP客户端
"""

import ftplib
import sys

def test_cwd():
    """测试CWD命令"""
    try:
        print("连接到FTP服务器...")
        ftp = ftplib.FTP()
        ftp.connect('localhost', 2121)
        
        print("登录...")
        ftp.login('admin', 'admin123')
        
        print("当前目录:")
        print(ftp.pwd())
        
        print("\n列出根目录内容:")
        ftp.retrlines('LIST')
        
        print("\n尝试切换到 /public 目录...")
        try:
            ftp.cwd('/public')
            print("成功切换到 /public 目录")
            print("当前目录:", ftp.pwd())
        except ftplib.error_perm as e:
            print(f"切换目录失败: {e}")
        
        print("\n尝试切换到 public 目录 (相对路径)...")
        try:
            ftp.cwd('/')  # 先回到根目录
            ftp.cwd('public')
            print("成功切换到 public 目录")
            print("当前目录:", ftp.pwd())
        except ftplib.error_perm as e:
            print(f"切换目录失败: {e}")
        
        ftp.quit()
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_cwd()
