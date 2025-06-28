#!/usr/bin/env python3
"""
Python FTP服务器
支持基本的FTP操作：上传、下载、目录浏览等
"""

import os
import sys
import socket
import threading
import time
from pathlib import Path
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ftp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FTPServer:
    """FTP服务器类"""
    
    def __init__(self, host='localhost', port=21, root_dir=None):
        self.host = host
        self.port = port
        self.root_dir = Path(root_dir) if root_dir else Path.cwd() / 'ftp_root'
        self.users = {
            'admin': 'admin123',
            'user': 'user123',
            'anonymous': ''
        }
        self.server_socket = None
        self.running = False
        
        # 确保根目录存在
        self.root_dir.mkdir(exist_ok=True)
        logger.info(f"FTP根目录: {self.root_dir.absolute()}")
    
    def start(self):
        """启动FTP服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            logger.info(f"FTP服务器启动成功: {self.host}:{self.port}")
            logger.info(f"支持的用户: {list(self.users.keys())}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"新客户端连接: {client_address}")
                    
                    # 为每个客户端创建新线程
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        logger.error(f"接受连接时出错: {e}")
                    
        except Exception as e:
            logger.error(f"启动FTP服务器失败: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止FTP服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("FTP服务器已停止")
    
    def handle_client(self, client_socket, client_address):
        """处理客户端连接"""
        session = FTPSession(client_socket, client_address, self.root_dir, self.users)
        session.handle()

class FTPSession:
    """FTP会话类"""
    
    def __init__(self, client_socket, client_address, root_dir, users):
        self.client_socket = client_socket
        self.client_address = client_address
        self.root_dir = root_dir
        self.users = users
        
        self.current_dir = root_dir
        self.authenticated = False
        self.username = None
        self.data_socket = None
        self.passive_socket = None
        
        # FTP命令映射
        self.commands = {
            'USER': self.cmd_user,
            'PASS': self.cmd_pass,
            'PWD': self.cmd_pwd,
            'CWD': self.cmd_cwd,
            'CDUP': self.cmd_cdup,
            'LIST': self.cmd_list,
            'RETR': self.cmd_retr,
            'STOR': self.cmd_stor,
            'DELE': self.cmd_dele,
            'MKD': self.cmd_mkd,
            'RMD': self.cmd_rmd,
            'PASV': self.cmd_pasv,
            'PORT': self.cmd_port,
            'TYPE': self.cmd_type,
            'QUIT': self.cmd_quit,
            'SYST': self.cmd_syst,
            'FEAT': self.cmd_feat,
        }
    
    def handle(self):
        """处理FTP会话"""
        try:
            # 发送欢迎消息
            self.send_response('220 Python FTP Server Ready')
            
            while True:
                try:
                    # 接收命令
                    data = self.client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break
                    
                    logger.info(f"[{self.client_address[0]}] 收到命令: {data}")
                    
                    # 解析命令
                    parts = data.split(' ', 1)
                    command = parts[0].upper()
                    args = parts[1] if len(parts) > 1 else ''
                    
                    # 执行命令
                    if command in self.commands:
                        self.commands[command](args)
                    else:
                        self.send_response('502 Command not implemented')
                        
                except socket.error:
                    break
                except Exception as e:
                    logger.error(f"处理命令时出错: {e}")
                    self.send_response('500 Internal server error')
                    
        except Exception as e:
            logger.error(f"处理客户端连接时出错: {e}")
        finally:
            self.cleanup()
    
    def send_response(self, message):
        """发送响应消息"""
        try:
            self.client_socket.send(f"{message}\r\n".encode('utf-8'))
            logger.info(f"[{self.client_address[0]}] 发送响应: {message}")
        except socket.error as e:
            logger.error(f"发送响应失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.data_socket:
                self.data_socket.close()
            if self.passive_socket:
                self.passive_socket.close()
            self.client_socket.close()
            logger.info(f"[{self.client_address[0]}] 连接已关闭")
        except:
            pass
    
    # FTP命令实现
    def cmd_user(self, username):
        """USER命令 - 设置用户名"""
        self.username = username
        if username in self.users:
            if self.users[username] == '':  # 匿名用户
                self.authenticated = True
                self.send_response('230 Anonymous login successful')
            else:
                self.send_response('331 Password required')
        else:
            self.send_response('530 Invalid username')
    
    def cmd_pass(self, password):
        """PASS命令 - 验证密码"""
        if not self.username:
            self.send_response('503 Login with USER first')
            return
        
        if self.username in self.users and self.users[self.username] == password:
            self.authenticated = True
            self.send_response('230 Login successful')
        else:
            self.send_response('530 Login incorrect')
    
    def cmd_pwd(self, args):
        """PWD命令 - 显示当前目录"""
        if not self.authenticated:
            self.send_response('530 Not logged in')
            return

        try:
            # 确保两个路径都是绝对路径
            root_abs = self.root_dir.resolve()
            current_abs = self.current_dir.resolve()

            rel_path = current_abs.relative_to(root_abs)
            path_str = '/' + str(rel_path).replace('\\', '/') if rel_path != Path('.') else '/'
            self.send_response(f'257 "{path_str}" is current directory')
        except Exception as e:
            logger.error(f"PWD命令错误: {e}")
            self.send_response('500 Internal server error')
    
    def cmd_cwd(self, path):
        """CWD命令 - 改变目录"""
        if not self.authenticated:
            self.send_response('530 Not logged in')
            return

        try:
            # 处理特殊路径
            if path == '..':
                # 返回上级目录
                new_dir = self.current_dir.parent
            elif path.startswith('/'):
                new_dir = self.root_dir / path[1:]
            else:
                new_dir = self.current_dir / path

            new_dir = new_dir.resolve()

            # 确保不能访问根目录之外的目录
            root_str = str(self.root_dir.resolve())
            new_str = str(new_dir)

            if not new_str.startswith(root_str):
                self.send_response('550 Permission denied')
                return

            if new_dir.is_dir():
                self.current_dir = new_dir
                self.send_response('250 Directory changed')
            else:
                self.send_response('550 Directory not found')

        except Exception as e:
            logger.error(f"CWD命令错误: {e}")
            self.send_response('550 Directory change failed')
    
    def cmd_list(self, args):
        """LIST命令 - 列出目录内容"""
        if not self.authenticated:
            self.send_response('530 Not logged in')
            return
        
        if not self.data_socket:
            self.send_response('425 Use PASV or PORT first')
            return
        
        try:
            self.send_response('150 Opening data connection')
            
            # 生成目录列表
            listing = []
            for item in self.current_dir.iterdir():
                stat = item.stat()
                mtime = datetime.fromtimestamp(stat.st_mtime)
                
                if item.is_dir():
                    listing.append(f"drwxr-xr-x 1 owner group {stat.st_size:>8} {mtime.strftime('%b %d %H:%M')} {item.name}")
                else:
                    listing.append(f"-rw-r--r-- 1 owner group {stat.st_size:>8} {mtime.strftime('%b %d %H:%M')} {item.name}")
            
            # 发送列表
            data = '\r\n'.join(listing) + '\r\n'
            self.data_socket.send(data.encode('utf-8'))
            self.data_socket.close()
            self.data_socket = None
            
            self.send_response('226 Transfer complete')
            
        except Exception as e:
            logger.error(f"LIST命令错误: {e}")
            self.send_response('550 List failed')
    
    def cmd_retr(self, filename):
        """RETR命令 - 下载文件"""
        if not self.authenticated:
            self.send_response('530 Not logged in')
            return
        
        if not self.data_socket:
            self.send_response('425 Use PASV or PORT first')
            return
        
        try:
            file_path = self.current_dir / filename
            
            if not file_path.exists() or not file_path.is_file():
                self.send_response('550 File not found')
                return
            
            self.send_response('150 Opening data connection')
            
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(8192)
                    if not data:
                        break
                    self.data_socket.send(data)
            
            self.data_socket.close()
            self.data_socket = None
            self.send_response('226 Transfer complete')
            
        except Exception as e:
            logger.error(f"RETR命令错误: {e}")
            self.send_response('550 Transfer failed')
    
    def cmd_stor(self, filename):
        """STOR命令 - 上传文件"""
        if not self.authenticated:
            self.send_response('530 Not logged in')
            return
        
        if not self.data_socket:
            self.send_response('425 Use PASV or PORT first')
            return
        
        try:
            file_path = self.current_dir / filename
            
            self.send_response('150 Opening data connection')
            
            with open(file_path, 'wb') as f:
                while True:
                    try:
                        data = self.data_socket.recv(8192)
                        if not data:
                            break
                        f.write(data)
                    except socket.timeout:
                        break
            
            self.data_socket.close()
            self.data_socket = None
            self.send_response('226 Transfer complete')
            
        except Exception as e:
            logger.error(f"STOR命令错误: {e}")
            self.send_response('550 Transfer failed')
    
    def cmd_dele(self, filename):
        """DELE命令 - 删除文件"""
        if not self.authenticated:
            self.send_response('530 Not logged in')
            return
        
        try:
            file_path = self.current_dir / filename
            
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                self.send_response('250 File deleted')
            else:
                self.send_response('550 File not found')
                
        except Exception as e:
            logger.error(f"DELE命令错误: {e}")
            self.send_response('550 Delete failed')
    
    def cmd_mkd(self, dirname):
        """MKD命令 - 创建目录"""
        if not self.authenticated:
            self.send_response('530 Not logged in')
            return
        
        try:
            dir_path = self.current_dir / dirname
            dir_path.mkdir()
            self.send_response('257 Directory created')
            
        except Exception as e:
            logger.error(f"MKD命令错误: {e}")
            self.send_response('550 Create directory failed')
    
    def cmd_rmd(self, dirname):
        """RMD命令 - 删除目录"""
        if not self.authenticated:
            self.send_response('530 Not logged in')
            return
        
        try:
            dir_path = self.current_dir / dirname
            
            if dir_path.exists() and dir_path.is_dir():
                dir_path.rmdir()
                self.send_response('250 Directory deleted')
            else:
                self.send_response('550 Directory not found')
                
        except Exception as e:
            logger.error(f"RMD命令错误: {e}")
            self.send_response('550 Remove directory failed')
    
    def cmd_pasv(self, args):
        """PASV命令 - 被动模式"""
        try:
            # 创建被动模式套接字
            self.passive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.passive_socket.bind((self.client_socket.getsockname()[0], 0))
            self.passive_socket.listen(1)
            
            # 获取端口号
            ip, port = self.passive_socket.getsockname()
            
            # 将IP地址转换为FTP格式
            ip_parts = ip.split('.')
            port_high = port // 256
            port_low = port % 256
            
            self.send_response(f'227 Entering Passive Mode ({",".join(ip_parts)},{port_high},{port_low})')
            
            # 等待数据连接
            self.data_socket, _ = self.passive_socket.accept()
            
        except Exception as e:
            logger.error(f"PASV命令错误: {e}")
            self.send_response('425 Cannot open passive connection')
    
    def cmd_port(self, args):
        """PORT命令 - 主动模式"""
        try:
            # 解析PORT参数
            parts = args.split(',')
            if len(parts) != 6:
                self.send_response('501 Invalid PORT command')
                return
            
            ip = '.'.join(parts[:4])
            port = int(parts[4]) * 256 + int(parts[5])
            
            # 创建数据连接
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.data_socket.connect((ip, port))
            
            self.send_response('200 PORT command successful')
            
        except Exception as e:
            logger.error(f"PORT命令错误: {e}")
            self.send_response('425 Cannot open data connection')
    
    def cmd_type(self, args):
        """TYPE命令 - 设置传输类型"""
        self.send_response('200 Type set to I')  # 二进制模式
    
    def cmd_syst(self, args):
        """SYST命令 - 系统信息"""
        self.send_response('215 UNIX Type: L8')
    
    def cmd_feat(self, args):
        """FEAT命令 - 功能列表"""
        features = [
            '211-Features:',
            ' PASV',
            ' PORT',
            ' TYPE I',
            '211 End'
        ]
        for feature in features:
            self.send_response(feature)
    
    def cmd_cdup(self, args):
        """CDUP命令 - 返回上级目录"""
        self.cmd_cwd('..')

    def cmd_quit(self, args):
        """QUIT命令 - 退出"""
        self.send_response('221 Goodbye')
        raise socket.error("Client quit")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Python FTP服务器')
    parser.add_argument('--host', default='localhost', help='服务器地址 (默认: localhost)')
    parser.add_argument('--port', type=int, default=2121, help='服务器端口 (默认: 2121)')
    parser.add_argument('--root', help='FTP根目录 (默认: ./ftp_root)')
    
    args = parser.parse_args()
    
    # 创建FTP服务器
    server = FTPServer(
        host=args.host,
        port=args.port,
        root_dir=args.root
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止服务器...")
        server.stop()

if __name__ == '__main__':
    main()
