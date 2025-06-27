# Python FTP服务器

一个功能完整的Python FTP服务器实现，支持基本的FTP操作，包括文件上传、下载、目录管理等功能。

## 功能特性

- ✅ 支持多用户认证
- ✅ 文件上传/下载
- ✅ 目录浏览和管理
- ✅ 被动模式(PASV)和主动模式(PORT)
- ✅ 完整的FTP命令支持
- ✅ 日志记录
- ✅ 配置文件管理
- ✅ 安全的目录访问控制

## 文件结构

```
├── ftp_server.py          # FTP服务器核心实现
├── ftp_client_test.py     # FTP客户端测试工具
├── start_ftp_server.py    # 服务器启动和管理脚本
├── ftp_config.json        # 配置文件(自动生成)
├── ftp_server.log         # 日志文件(自动生成)
└── ftp_root/              # FTP根目录(自动创建)
    ├── uploads/           # 上传目录
    ├── downloads/         # 下载目录
    ├── public/            # 公共目录
    └── README.txt         # 说明文件
```

## 快速开始

### 1. 启动FTP服务器

```bash
# 使用默认配置启动
python start_ftp_server.py start

# 自定义配置启动
python start_ftp_server.py start --host 0.0.0.0 --port 2121 --root ./my_ftp_root
```

### 2. 查看服务器状态

```bash
python start_ftp_server.py status
```

### 3. 运行测试

```bash
# 自动测试
python start_ftp_server.py test

# 或直接使用测试脚本
python ftp_client_test.py --test

# 交互式客户端
python ftp_client_test.py --interactive
```

## 配置说明

### 默认用户账户

| 用户名 | 密码 | 权限 | 说明 |
|--------|------|------|------|
| admin | admin123 | 读写删除 | 管理员账户 |
| user | user123 | 读写 | 普通用户 |
| anonymous | (无) | 只读 | 匿名用户 |

### 配置文件 (ftp_config.json)

```json
{
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
```

## 支持的FTP命令

| 命令 | 说明 | 示例 |
|------|------|------|
| USER | 设置用户名 | `USER admin` |
| PASS | 验证密码 | `PASS admin123` |
| PWD | 显示当前目录 | `PWD` |
| CWD | 改变目录 | `CWD uploads` |
| LIST | 列出目录内容 | `LIST` |
| RETR | 下载文件 | `RETR filename.txt` |
| STOR | 上传文件 | `STOR filename.txt` |
| DELE | 删除文件 | `DELE filename.txt` |
| MKD | 创建目录 | `MKD newdir` |
| RMD | 删除目录 | `RMD olddir` |
| PASV | 被动模式 | `PASV` |
| PORT | 主动模式 | `PORT 192,168,1,100,20,21` |
| TYPE | 设置传输类型 | `TYPE I` |
| SYST | 系统信息 | `SYST` |
| FEAT | 功能列表 | `FEAT` |
| QUIT | 退出连接 | `QUIT` |

## 使用示例

### 使用标准FTP客户端连接

```bash
# Windows命令行
ftp localhost 2121

# Linux/Mac
ftp localhost 2121
```

### 使用Python ftplib

```python
import ftplib

# 连接服务器
ftp = ftplib.FTP()
ftp.connect('localhost', 2121)

# 登录
ftp.login('admin', 'admin123')

# 列出目录
ftp.retrlines('LIST')

# 上传文件
with open('local_file.txt', 'rb') as f:
    ftp.storbinary('STOR remote_file.txt', f)

# 下载文件
with open('downloaded_file.txt', 'wb') as f:
    ftp.retrbinary('RETR remote_file.txt', f.write)

# 关闭连接
ftp.quit()
```

### 使用FileZilla等图形化客户端

1. 打开FileZilla
2. 主机: `localhost`
3. 端口: `2121`
4. 用户名: `admin`
5. 密码: `admin123`
6. 点击"快速连接"

## 高级配置

### 修改配置

```bash
# 生成新的配置文件
python start_ftp_server.py config

# 自定义配置
python start_ftp_server.py config --host 0.0.0.0 --port 21 --root /var/ftp
```

### 添加新用户

编辑 `ftp_config.json` 文件，在 `users` 部分添加新用户：

```json
"newuser": {
  "password": "newpassword",
  "permissions": ["read", "write"]
}
```

### 日志配置

日志文件默认保存在 `ftp_server.log`，包含以下信息：
- 客户端连接/断开
- 用户登录
- 文件操作
- 错误信息

## 安全注意事项

1. **密码安全**: 修改默认密码，使用强密码
2. **网络安全**: 生产环境建议使用FTPS或SFTP
3. **目录权限**: 确保FTP根目录权限设置正确
4. **防火墙**: 配置防火墙规则，只允许必要的端口访问
5. **用户权限**: 根据需要限制用户权限

## 故障排除

### 常见问题

1. **端口被占用**
   ```
   错误: [Errno 10048] Only one usage of each socket address
   解决: 更改端口号或停止占用端口的程序
   ```

2. **权限不足**
   ```
   错误: Permission denied
   解决: 检查FTP根目录权限，确保有读写权限
   ```

3. **连接被拒绝**
   ```
   错误: Connection refused
   解决: 检查服务器是否启动，防火墙设置
   ```

### 调试模式

启用详细日志记录：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 性能优化

1. **并发连接**: 服务器支持多线程处理多个客户端
2. **缓冲区大小**: 默认8KB，可根据需要调整
3. **超时设置**: 可配置连接超时时间

## 扩展功能

可以基于现有代码扩展以下功能：
- SSL/TLS支持 (FTPS)
- 虚拟用户系统
- 配额管理
- 带宽限制
- 访问日志分析
- Web管理界面

## 许可证

本项目采用MIT许可证，可自由使用和修改。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 创建GitHub Issue
- 发送邮件至项目维护者
