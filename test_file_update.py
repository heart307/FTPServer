#!/usr/bin/env python3
"""
测试文件更新后客户端是否能看到的脚本
"""

import ftplib
import time
import os
import tempfile
from pathlib import Path

def test_file_update_visibility():
    """测试文件更新后的可见性"""
    print("=" * 60)
    print("测试FTP服务器文件更新可见性")
    print("=" * 60)
    
    try:
        # 连接FTP服务器
        print("\n1. 连接FTP服务器...")
        ftp = ftplib.FTP()
        ftp.connect('localhost', 2121)
        ftp.login('admin', 'admin123')
        print("✅ 连接成功")
        
        # 切换到uploads目录
        print("\n2. 切换到uploads目录...")
        ftp.cwd('/uploads')
        print(f"✅ 当前目录: {ftp.pwd()}")
        
        # 查看初始文件列表
        print("\n3. 查看初始文件列表...")
        print("初始文件列表:")
        files_before = []
        def collect_files(line):
            files_before.append(line)
            print(f"  {line}")
        ftp.retrlines('LIST', collect_files)
        
        # 在服务器端直接创建一个文件
        print("\n4. 在服务器端直接创建文件...")
        server_file_path = Path("ftp_root/uploads/server_created_file.txt")
        with open(server_file_path, 'w', encoding='utf-8') as f:
            f.write("这是在服务器端直接创建的文件\n")
            f.write(f"创建时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"✅ 在服务器端创建文件: {server_file_path}")
        
        # 立即查看文件列表
        print("\n5. 立即查看文件列表...")
        print("更新后的文件列表:")
        files_after_immediate = []
        def collect_files_immediate(line):
            files_after_immediate.append(line)
            print(f"  {line}")
        ftp.retrlines('LIST', collect_files_immediate)
        
        # 等待一段时间后再查看
        print("\n6. 等待2秒后再次查看文件列表...")
        time.sleep(2)
        print("等待2秒后的文件列表:")
        files_after_wait = []
        def collect_files_wait(line):
            files_after_wait.append(line)
            print(f"  {line}")
        ftp.retrlines('LIST', collect_files_wait)
        
        # 通过FTP上传一个文件
        print("\n7. 通过FTP上传文件...")
        test_content = f"FTP上传的测试文件\n上传时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_content)
            temp_file = f.name
        
        with open(temp_file, 'rb') as f:
            ftp.storbinary('STOR ftp_uploaded_file.txt', f)
        os.unlink(temp_file)
        print("✅ FTP上传文件成功")
        
        # 查看上传后的文件列表
        print("\n8. 查看FTP上传后的文件列表...")
        print("FTP上传后的文件列表:")
        files_after_ftp = []
        def collect_files_ftp(line):
            files_after_ftp.append(line)
            print(f"  {line}")
        ftp.retrlines('LIST', collect_files_ftp)
        
        # 在服务器端修改已存在的文件
        print("\n9. 在服务器端修改文件...")
        if server_file_path.exists():
            with open(server_file_path, 'a', encoding='utf-8') as f:
                f.write(f"修改时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            print(f"✅ 修改服务器端文件: {server_file_path}")
        
        # 查看修改后的文件列表
        print("\n10. 查看修改后的文件列表...")
        print("修改后的文件列表:")
        files_after_modify = []
        def collect_files_modify(line):
            files_after_modify.append(line)
            print(f"  {line}")
        ftp.retrlines('LIST', collect_files_modify)
        
        # 尝试下载服务器端创建的文件
        print("\n11. 尝试下载服务器端创建的文件...")
        try:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
                ftp.retrbinary('RETR server_created_file.txt', f.write)
                download_file = f.name
            
            with open(download_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ 下载成功，文件内容:\n{content}")
            os.unlink(download_file)
        except Exception as e:
            print(f"❌ 下载失败: {e}")
        
        # 分析结果
        print("\n" + "=" * 60)
        print("分析结果:")
        print("=" * 60)
        
        print(f"初始文件数量: {len(files_before)}")
        print(f"服务器端创建文件后立即查看: {len(files_after_immediate)}")
        print(f"等待2秒后查看: {len(files_after_wait)}")
        print(f"FTP上传后查看: {len(files_after_ftp)}")
        print(f"服务器端修改后查看: {len(files_after_modify)}")
        
        # 检查是否能看到服务器端创建的文件
        server_file_visible = any('server_created_file.txt' in line for line in files_after_immediate)
        ftp_file_visible = any('ftp_uploaded_file.txt' in line for line in files_after_ftp)
        
        print(f"\n服务器端创建的文件是否可见: {'✅ 是' if server_file_visible else '❌ 否'}")
        print(f"FTP上传的文件是否可见: {'✅ 是' if ftp_file_visible else '❌ 否'}")
        
        # 清理测试文件
        print("\n12. 清理测试文件...")
        try:
            ftp.delete('server_created_file.txt')
            ftp.delete('ftp_uploaded_file.txt')
            print("✅ 清理完成")
        except Exception as e:
            print(f"⚠️ 清理时出现错误: {e}")
        
        ftp.quit()
        
        return server_file_visible and ftp_file_visible
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_file_update_visibility()
    if success:
        print("\n🎉 测试通过：文件更新可见性正常")
    else:
        print("\n❌ 测试失败：存在文件更新可见性问题")
