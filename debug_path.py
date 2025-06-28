#!/usr/bin/env python3
"""
调试路径问题的脚本
"""

from pathlib import Path
import os

def debug_path_issue():
    """调试路径问题"""
    print("=== 调试路径问题 ===")
    
    # 模拟FTP服务器的路径处理
    root_dir = Path("./ftp_root").resolve()
    print(f"FTP根目录: {root_dir}")
    print(f"FTP根目录字符串: {str(root_dir)}")
    
    # 模拟CWD /public命令
    path = "/public"
    print(f"\n处理路径: {path}")
    
    if path.startswith('/'):
        new_dir = root_dir / path[1:]
    else:
        new_dir = root_dir / path
    
    print(f"拼接后路径: {new_dir}")
    
    new_dir = new_dir.resolve()
    print(f"解析后路径: {new_dir}")
    print(f"解析后路径字符串: {str(new_dir)}")
    
    # 检查权限
    print(f"\n权限检查:")
    print(f"根目录字符串: '{str(root_dir)}'")
    print(f"新目录字符串: '{str(new_dir)}'")
    print(f"新目录是否以根目录开头: {str(new_dir).startswith(str(root_dir))}")
    
    # 检查目录是否存在
    print(f"\n目录检查:")
    print(f"新目录是否存在: {new_dir.exists()}")
    print(f"新目录是否为目录: {new_dir.is_dir()}")
    
    # 检查public目录的实际情况
    public_dir = root_dir / "public"
    print(f"\npublic目录:")
    print(f"public目录路径: {public_dir}")
    print(f"public目录是否存在: {public_dir.exists()}")
    print(f"public目录是否为目录: {public_dir.is_dir()}")
    
    # 列出根目录内容
    print(f"\n根目录内容:")
    if root_dir.exists():
        for item in root_dir.iterdir():
            print(f"  {item.name} ({'目录' if item.is_dir() else '文件'})")
    
    # 测试路径比较的不同方法
    print(f"\n路径比较测试:")
    print(f"方法1 - 字符串比较: {str(new_dir).startswith(str(root_dir))}")
    
    # 使用resolve()后的路径比较
    try:
        new_dir.relative_to(root_dir)
        print(f"方法2 - relative_to: True")
    except ValueError:
        print(f"方法2 - relative_to: False")
    
    # 使用is_relative_to (Python 3.9+)
    try:
        print(f"方法3 - is_relative_to: {new_dir.is_relative_to(root_dir)}")
    except AttributeError:
        print(f"方法3 - is_relative_to: 不支持 (Python < 3.9)")

if __name__ == "__main__":
    debug_path_issue()
