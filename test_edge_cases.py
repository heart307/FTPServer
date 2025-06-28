#!/usr/bin/env python3
"""
测试FTP服务器的边缘情况和潜在问题
"""

import ftplib
import time
import os
import tempfile
from pathlib import Path
import threading

def test_concurrent_access():
    """测试并发访问时的文件可见性"""
    print("\n" + "=" * 60)
    print("测试并发访问时的文件可见性")
    print("=" * 60)
    
    def client_thread(client_id):
        """客户端线程"""
        try:
            ftp = ftplib.FTP()
            ftp.connect('localhost', 2121)
            ftp.login('admin', 'admin123')
            ftp.cwd('/uploads')
            
            # 创建文件
            filename = f'client_{client_id}_file.txt'
            content = f'Client {client_id} created this file at {time.strftime("%Y-%m-%d %H:%M:%S")}\n'
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                f.write(content)
                temp_file = f.name
            
            with open(temp_file, 'rb') as f:
                ftp.storbinary(f'STOR {filename}', f)
            os.unlink(temp_file)
            
            print(f"✅ 客户端 {client_id} 创建文件: {filename}")
            
            # 查看文件列表
            files = []
            ftp.retrlines('LIST', files.append)
            client_files = [line for line in files if f'client_{client_id}_file.txt' in line]
            
            if client_files:
                print(f"✅ 客户端 {client_id} 可以看到自己创建的文件")
            else:
                print(f"❌ 客户端 {client_id} 看不到自己创建的文件")
            
            ftp.quit()
            
        except Exception as e:
            print(f"❌ 客户端 {client_id} 出错: {e}")
    
    # 启动多个客户端线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=client_thread, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()

def test_special_characters():
    """测试特殊字符文件名"""
    print("\n" + "=" * 60)
    print("测试特殊字符文件名")
    print("=" * 60)
    
    try:
        ftp = ftplib.FTP()
        ftp.connect('localhost', 2121)
        ftp.login('admin', 'admin123')
        ftp.cwd('/uploads')
        
        # 测试不同的文件名
        test_filenames = [
            'normal_file.txt',
            'file with spaces.txt',
            'file-with-dashes.txt',
            'file_with_underscores.txt',
            'file.with.dots.txt',
            'UPPERCASE.TXT',
            'MixedCase.Txt',
        ]
        
        created_files = []
        
        for filename in test_filenames:
            try:
                content = f'Test file: {filename}\nCreated at: {time.strftime("%Y-%m-%d %H:%M:%S")}\n'
                
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                    f.write(content)
                    temp_file = f.name
                
                with open(temp_file, 'rb') as f:
                    ftp.storbinary(f'STOR {filename}', f)
                os.unlink(temp_file)
                
                created_files.append(filename)
                print(f"✅ 创建文件: {filename}")
                
            except Exception as e:
                print(f"❌ 创建文件失败 {filename}: {e}")
        
        # 查看文件列表
        print("\n查看文件列表:")
        files = []
        ftp.retrlines('LIST', files.append)
        
        for filename in created_files:
            found = any(filename in line for line in files)
            if found:
                print(f"✅ 可见: {filename}")
            else:
                print(f"❌ 不可见: {filename}")
        
        # 清理文件
        print("\n清理测试文件...")
        for filename in created_files:
            try:
                ftp.delete(filename)
                print(f"✅ 删除: {filename}")
            except Exception as e:
                print(f"❌ 删除失败 {filename}: {e}")
        
        ftp.quit()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_directory_operations():
    """测试目录操作"""
    print("\n" + "=" * 60)
    print("测试目录操作")
    print("=" * 60)
    
    try:
        ftp = ftplib.FTP()
        ftp.connect('localhost', 2121)
        ftp.login('admin', 'admin123')
        ftp.cwd('/uploads')
        
        # 创建测试目录
        test_dir = 'test_directory'
        try:
            ftp.mkd(test_dir)
            print(f"✅ 创建目录: {test_dir}")
        except Exception as e:
            print(f"❌ 创建目录失败: {e}")
            return
        
        # 查看目录是否可见
        files = []
        ftp.retrlines('LIST', files.append)
        dir_visible = any(test_dir in line and line.startswith('d') for line in files)
        
        if dir_visible:
            print(f"✅ 目录可见: {test_dir}")
        else:
            print(f"❌ 目录不可见: {test_dir}")
        
        # 进入目录
        try:
            ftp.cwd(test_dir)
            print(f"✅ 进入目录: {test_dir}")
            print(f"当前目录: {ftp.pwd()}")
        except Exception as e:
            print(f"❌ 进入目录失败: {e}")
            return
        
        # 在目录中创建文件
        filename = 'file_in_subdir.txt'
        content = f'File in subdirectory\nCreated at: {time.strftime("%Y-%m-%d %H:%M:%S")}\n'
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(content)
            temp_file = f.name
        
        with open(temp_file, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)
        os.unlink(temp_file)
        
        print(f"✅ 在子目录中创建文件: {filename}")
        
        # 查看子目录内容
        files = []
        ftp.retrlines('LIST', files.append)
        file_visible = any(filename in line for line in files)
        
        if file_visible:
            print(f"✅ 子目录中的文件可见: {filename}")
        else:
            print(f"❌ 子目录中的文件不可见: {filename}")
        
        # 返回上级目录
        ftp.cwd('..')
        print(f"✅ 返回上级目录: {ftp.pwd()}")
        
        # 清理
        ftp.cwd(test_dir)
        ftp.delete(filename)
        ftp.cwd('..')
        ftp.rmd(test_dir)
        print("✅ 清理完成")
        
        ftp.quit()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_file_permissions():
    """测试文件权限问题"""
    print("\n" + "=" * 60)
    print("测试文件权限")
    print("=" * 60)
    
    # 在服务器端创建不同权限的文件
    uploads_dir = Path("ftp_root/uploads")
    
    # 创建只读文件
    readonly_file = uploads_dir / "readonly_file.txt"
    with open(readonly_file, 'w', encoding='utf-8') as f:
        f.write("这是一个只读文件\n")
    
    # 在Windows上设置只读属性
    try:
        os.chmod(readonly_file, 0o444)  # 只读权限
        print(f"✅ 创建只读文件: {readonly_file}")
    except Exception as e:
        print(f"⚠️ 设置只读权限失败: {e}")
    
    try:
        ftp = ftplib.FTP()
        ftp.connect('localhost', 2121)
        ftp.login('admin', 'admin123')
        ftp.cwd('/uploads')
        
        # 查看文件列表
        files = []
        ftp.retrlines('LIST', files.append)
        
        readonly_visible = any('readonly_file.txt' in line for line in files)
        if readonly_visible:
            print("✅ 只读文件在FTP中可见")
        else:
            print("❌ 只读文件在FTP中不可见")
        
        # 尝试下载只读文件
        try:
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
                ftp.retrbinary('RETR readonly_file.txt', f.write)
                download_file = f.name
            
            with open(download_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ 成功下载只读文件，内容: {repr(content)}")
            os.unlink(download_file)
            
        except Exception as e:
            print(f"❌ 下载只读文件失败: {e}")
        
        ftp.quit()
        
        # 清理
        try:
            os.chmod(readonly_file, 0o666)  # 恢复写权限
            readonly_file.unlink()
            print("✅ 清理只读文件")
        except Exception as e:
            print(f"⚠️ 清理只读文件失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主测试函数"""
    print("FTP服务器边缘情况测试")
    print("=" * 60)
    
    test_concurrent_access()
    test_special_characters()
    test_directory_operations()
    test_file_permissions()
    
    print("\n" + "=" * 60)
    print("所有边缘情况测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
