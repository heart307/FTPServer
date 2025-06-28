#!/usr/bin/env python3
"""
全面测试FTP服务器功能
"""

import ftplib
import sys
import os
import tempfile

def comprehensive_test():
    """全面测试FTP服务器功能"""
    try:
        print("=" * 50)
        print("FTP服务器功能全面测试")
        print("=" * 50)
        
        print("\n1. 连接到FTP服务器...")
        ftp = ftplib.FTP()
        ftp.connect('localhost', 2121)
        print("✅ 连接成功")
        
        print("\n2. 登录...")
        ftp.login('admin', 'admin123')
        print("✅ 登录成功")
        
        print("\n3. 测试PWD命令...")
        current_dir = ftp.pwd()
        print(f"✅ 当前目录: {current_dir}")
        
        print("\n4. 测试LIST命令...")
        print("根目录内容:")
        ftp.retrlines('LIST')
        print("✅ LIST命令成功")
        
        print("\n5. 测试CWD命令 - 绝对路径...")
        try:
            ftp.cwd('/public')
            current_dir = ftp.pwd()
            print(f"✅ 成功切换到 /public，当前目录: {current_dir}")
        except ftplib.error_perm as e:
            print(f"❌ 切换到 /public 失败: {e}")
            return False
        
        print("\n6. 测试CWD命令 - 返回根目录...")
        try:
            ftp.cwd('/')
            current_dir = ftp.pwd()
            print(f"✅ 成功返回根目录，当前目录: {current_dir}")
        except ftplib.error_perm as e:
            print(f"❌ 返回根目录失败: {e}")
            return False
        
        print("\n7. 测试CWD命令 - 相对路径...")
        try:
            ftp.cwd('downloads')
            current_dir = ftp.pwd()
            print(f"✅ 成功切换到 downloads，当前目录: {current_dir}")
        except ftplib.error_perm as e:
            print(f"❌ 切换到 downloads 失败: {e}")
            return False
        
        print("\n8. 测试上传文件...")
        try:
            # 创建一个临时测试文件
            test_content = "这是一个测试文件\nFTP上传测试\n"
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(test_content)
                temp_file = f.name
            
            with open(temp_file, 'rb') as f:
                ftp.storbinary('STOR test_upload.txt', f)
            
            os.unlink(temp_file)  # 删除临时文件
            print("✅ 文件上传成功")
        except Exception as e:
            print(f"❌ 文件上传失败: {e}")
        
        print("\n9. 测试下载文件...")
        try:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
                ftp.retrbinary('RETR test_upload.txt', f.write)
                download_file = f.name
            
            with open(download_file, 'r') as f:
                content = f.read()
                print(f"✅ 文件下载成功，内容: {repr(content)}")
            
            os.unlink(download_file)  # 删除下载的文件
        except Exception as e:
            print(f"❌ 文件下载失败: {e}")
        
        print("\n10. 测试目录创建...")
        try:
            ftp.mkd('test_directory')
            print("✅ 目录创建成功")
        except Exception as e:
            print(f"❌ 目录创建失败: {e}")
        
        print("\n11. 测试进入新创建的目录...")
        try:
            ftp.cwd('test_directory')
            current_dir = ftp.pwd()
            print(f"✅ 成功进入新目录，当前目录: {current_dir}")
        except Exception as e:
            print(f"❌ 进入新目录失败: {e}")
        
        print("\n12. 测试返回上级目录...")
        try:
            ftp.cwd('..')
            current_dir = ftp.pwd()
            print(f"✅ 成功返回上级目录，当前目录: {current_dir}")
        except Exception as e:
            print(f"❌ 返回上级目录失败: {e}")
        
        print("\n13. 测试删除文件...")
        try:
            ftp.delete('test_upload.txt')
            print("✅ 文件删除成功")
        except Exception as e:
            print(f"❌ 文件删除失败: {e}")
        
        print("\n14. 测试删除目录...")
        try:
            ftp.rmd('test_directory')
            print("✅ 目录删除成功")
        except Exception as e:
            print(f"❌ 目录删除失败: {e}")
        
        print("\n15. 断开连接...")
        ftp.quit()
        print("✅ 断开连接成功")
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！FTP服务器功能正常")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = comprehensive_test()
    sys.exit(0 if success else 1)
