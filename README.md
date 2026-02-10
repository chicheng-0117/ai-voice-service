# LiveKit 多 Agent 语音助手系统 - API 服务

基于 LiveKit 的多 Agent 语音助手系统 API 服务，支持多个独立的语音角色（如 Peppa Pig、George 等）。

## 项目结构

```
ai-voice-service/
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── api_response.py     # 统一响应模型
│   ├── room_models.py      # 房间相关模型
│   └── token_models.py     # Token相关模型
├── services/               # 服务层
│   ├── __init__.py
│   └── room_service.py    # 房间管理服务
├── tests/                  # 测试
│   ├── __init__.py
│   ├── conftest.py         # Pytest配置
│   ├── test_models.py      # 模型测试
│   └── test_api.py         # API测试
├── main.py                 # FastAPI应用入口
├── pyproject.toml          # 项目配置和依赖
├── Makefile                # 常用命令
├── .pre-commit-config.yaml # Pre-commit配置
├── Dockerfile              # Docker配置
├── env.example             # 环境变量示例
└── README.md
```

## 快速开始

### 1. 安装依赖

使用 uv（推荐）：
```bash
uv sync
```

或使用 pip：
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env.example` 为 `.env.local` 并填入实际值：

```bash
cp env.example .env.local
```

编辑 `.env.local`，填入你的 LiveKit 配置：
```env
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

### 3. 运行服务

```bash
# 方式1：使用 uvicorn
uvicorn api_server.main:app --host 0.0.0.0 --port 8000 --reload

# 方式2：直接运行
python -m api_server.main
```

服务启动后，访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## API 端点

### 列出可用 Agent
```
GET /api/agents
```

### 创建房间
```
POST /api/rooms/create
Content-Type: application/json

{
  "agent_name": "peppa",
  "user_id": "user123",  // 可选
  "timeout_minutes": 60  // 可选，默认60分钟
}
```

### 加入房间
```
POST /api/rooms/join
Content-Type: application/json

{
  "room_name": "room-peppa-abc123",
  "user_id": "user123"  // 可选
}
```

### 获取房间信息
```
GET /api/rooms/{room_name}
```

### 删除房间
```
DELETE /api/rooms/{room_name}
```

## 开发

### 安装开发环境

```bash
# 安装所有依赖（包括开发依赖）
make install-dev

# 或使用 uv
uv sync
```

### 开发工具

项目使用以下工具保证代码质量：

- **Ruff** - 快速 Python linter 和格式化工具
- **MyPy** - 静态类型检查
- **Pytest** - 测试框架
- **Pre-commit** - Git 提交前检查

### 常用命令

使用 `make` 命令（推荐）：

```bash
make help          # 显示所有可用命令
make install-dev   # 安装开发依赖
make test          # 运行测试
make lint          # 代码检查
make format        # 格式化代码
make type-check    # 类型检查
make check         # 运行所有检查
make dev           # 启动开发服务器
make clean         # 清理生成的文件
```

或直接使用命令：

```bash
# 代码检查
ruff check .
ruff format .

# 类型检查
mypy .

# 运行测试
pytest
pytest --cov=. --cov-report=html  # 带覆盖率

# 启动开发服务器
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Pre-commit 钩子

安装 pre-commit 钩子（提交代码前自动检查）：

```bash
pre-commit install
```

### 项目依赖

**生产依赖：**
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `livekit` - LiveKit SDK
- `python-dotenv` - 环境变量管理
- `pydantic` - 数据验证

**开发依赖：**
- `pytest` - 测试框架
- `ruff` - 代码检查和格式化
- `mypy` - 类型检查
- `pre-commit` - Git 钩子

## Docker 部署

### 构建镜像

```bash
make docker-build
# 或
docker build -t ai-voice-service:latest .
```

### 运行容器

```bash
make docker-run
# 或
docker run -p 8000:8000 --env-file .env.local ai-voice-service:latest
```

## CI/CD

项目配置了 GitHub Actions CI，在每次推送和 PR 时会自动运行：
- 代码检查（Ruff）
- 类型检查（MyPy）
- 测试（Pytest）
- 覆盖率报告

## 详细文档

- [API 接口文档](./API_DOCUMENTATION.md) - 完整的 API 接口说明
- [服务文档](./API_SERVICE_DOCUMENTATION.md) - 系统架构和实现细节
- [配置说明](./CONFIGURATION.md) - 环境变量配置和故障排查

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License

