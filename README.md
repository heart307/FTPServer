# FTP文件传输管理系统

一个基于Flask和React的现代化FTP文件传输管理系统，支持多站点管理、任务优先级调度、文件夹监控等高级功能。

## 功能特性

### 核心功能
- 🌐 **多站点管理** - 支持管理多个FTP/FTPS/SFTP服务器
- 📁 **文件夹操作** - 支持文件夹批量下载和实时监控
- ⚡ **任务优先级** - 五级优先级系统，智能任务调度
- 📊 **实时监控** - 实时进度显示和资源监控
- 📝 **日志管理** - 完整的操作日志和审计追踪

### 高级特性
- 🔄 **断点续传** - 支持大文件断点续传
- 🚀 **并发传输** - 多线程并发文件传输
- 📈 **带宽控制** - 智能带宽分配和限制
- 🔍 **增量同步** - 文件夹变更检测和增量下载
- 🛡️ **安全认证** - JWT认证和权限管理

## 技术栈

### 后端
- **Flask** - Web框架
- **SQLAlchemy** - ORM数据库操作
- **Celery** - 异步任务处理
- **Redis** - 缓存和消息队列
- **Flask-SocketIO** - 实时通信

### 前端
- **React 18** - 前端框架
- **TypeScript** - 类型安全
- **Ant Design** - UI组件库
- **Redux Toolkit** - 状态管理
- **Socket.IO** - 实时通信

### 数据库
- **SQLite** (开发环境)
- **PostgreSQL** (生产环境)

## 项目结构

```
ftp-manager/
├── backend/                 # Flask后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/         # 数据库模型
│   │   ├── api/           # API接口
│   │   ├── core/          # 核心业务逻辑
│   │   ├── utils/         # 工具函数
│   │   └── config.py      # 配置文件
│   ├── migrations/        # 数据库迁移
│   ├── tests/            # 测试文件
│   ├── requirements.txt  # Python依赖
│   └── run.py           # 启动文件
├── frontend/              # React前端
│   ├── src/
│   │   ├── components/   # React组件
│   │   ├── pages/       # 页面组件
│   │   ├── store/       # Redux状态管理
│   │   ├── services/    # API服务
│   │   ├── utils/       # 工具函数
│   │   └── types/       # TypeScript类型定义
│   ├── public/          # 静态资源
│   ├── package.json     # 前端依赖
│   └── vite.config.ts   # Vite配置
├── docker-compose.yml    # Docker编排
├── nginx.conf           # Nginx配置
└── README.md           # 项目说明
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+ (可选，用于前端开发)
- Redis 6+ (可选，用于生产环境)
- PostgreSQL 12+ (可选，用于生产环境)

### 一键启动开发环境

1. **克隆项目**
```bash
git clone <repository-url>
cd ftp-manager
```

2. **使用一键启动脚本**
```bash
# 自动安装依赖并启动服务
python start_dev.py
```

这个脚本会自动：
- 检查Python环境
- 安装后端依赖
- 初始化SQLite数据库
- 启动Flask后端服务 (http://localhost:5000)
- 启动React前端服务 (http://localhost:3000，如果有Node.js)

### 手动启动（高级用户）

1. **后端设置**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **前端设置**（可选）
```bash
cd frontend
npm install
```

3. **启动服务**
```bash
# 启动后端
cd backend
python run.py

# 启动前端（可选）
cd frontend
npm run dev
```

### 默认账户
系统启动后，可以通过注册功能创建账户，或者使用以下默认管理员账户：
- 用户名: admin
- 密码: admin123

### Docker部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 配置说明

### 环境变量
```bash
# 数据库配置
DATABASE_URL=sqlite:///app.db
REDIS_URL=redis://localhost:6379/0

# JWT配置
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# 文件存储
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=1073741824  # 1GB

# 调度器配置
MAX_CONCURRENT_TASKS=10
MAX_FTP_CONNECTIONS=20
DEFAULT_BANDWIDTH_LIMIT=10240  # KB/s
```

## API文档

启动服务后访问 `http://localhost:5000/api/docs` 查看完整的API文档。

## 许可证

MIT License
