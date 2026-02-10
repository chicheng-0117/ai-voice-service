# 第一次提交代码指南

## ✅ 应该提交的文件

### 源代码
- ✅ `main.py` - 应用入口
- ✅ `models/` - 所有模型文件
- ✅ `services/` - 所有服务文件

### 配置文件
- ✅ `pyproject.toml` - 项目配置和依赖
- ✅ `uv.lock` - 依赖锁定文件（确保版本一致）
- ✅ `.gitignore` - Git 忽略规则
- ✅ `.gitattributes` - Git 属性配置
- ✅ `Dockerfile` - Docker 配置
- ✅ `.dockerignore` - Docker 忽略规则（如果存在）

### 文档
- ✅ `README.md` - 项目说明
- ✅ `env.example` - 环境变量示例（**重要：不要提交 .env.local**）

### 其他
- ✅ `.python-version` - Python 版本（如果使用 pyenv，可选）

## ❌ 不应该提交的文件

### 敏感信息
- ❌ `.env.local` - **包含敏感信息，绝对不能提交！**
- ❌ `.env` - 环境变量文件
- ❌ 任何包含 API Key、Secret 的文件

### 生成的文件
- ❌ `__pycache__/` - Python 缓存目录
- ❌ `*.pyc`, `*.pyo` - Python 编译文件
- ❌ `.pytest_cache/` - 测试缓存
- ❌ `.ruff_cache/` - Ruff 缓存
- ❌ `.mypy_cache/` - MyPy 缓存
- ❌ `htmlcov/` - 覆盖率报告
- ❌ `.coverage` - 覆盖率数据

### 虚拟环境
- ❌ `.venv/` - 虚拟环境目录
- ❌ `venv/` - 虚拟环境目录
- ❌ `ENV/` - 虚拟环境目录

### IDE 配置
- ❌ `.vscode/` - VS Code 配置（个人偏好）
- ❌ `.idea/` - PyCharm 配置（个人偏好）

### 构建产物
- ❌ `build/` - 构建目录
- ❌ `dist/` - 分发目录
- ❌ `*.egg-info/` - 包信息

## 📝 第一次提交步骤

### 1. 检查当前状态

```bash
# 查看所有未跟踪的文件
git status

# 查看会被提交的文件
git status --short
```

### 2. 确认敏感文件不会被提交

```bash
# 检查 .env.local 是否在 .gitignore 中
git check-ignore .env.local

# 如果返回 .env.local，说明已被忽略，安全
```

### 3. 添加文件到暂存区

```bash
# 添加所有应该提交的文件（.gitignore 会自动排除不应该提交的文件）
git add .

# 或者更安全的方式，逐个添加
git add .gitignore
git add .gitattributes
git add pyproject.toml
git add uv.lock
git add README.md
git add env.example
git add Dockerfile
git add main.py
git add models/
git add services/
```

### 4. 检查暂存区内容

```bash
# 查看将要提交的文件
git status

# 查看详细的变更
git diff --cached
```

### 5. 提交代码

```bash
# 提交（使用有意义的提交信息）
git commit -m "feat: 初始提交 - LiveKit 多 Agent 语音助手 API 服务

- 添加 FastAPI 应用和路由
- 实现房间管理服务
- 添加统一响应模型
- 配置项目依赖和开发工具
- 添加 Docker 支持"
```

### 6. 推送到远程仓库

```bash
# 如果还没有设置远程仓库
git remote add origin <your-repo-url>

# 推送到远程仓库
git push -u origin master
# 或
git push -u origin main
```

## 🔒 安全检查清单

在提交前，请确认：

- [ ] `.env.local` 文件不存在或已被 `.gitignore` 忽略
- [ ] 没有硬编码的 API Key 或 Secret
- [ ] `__pycache__/` 目录已被忽略
- [ ] 虚拟环境目录（`.venv/`, `venv/`）已被忽略
- [ ] 没有提交个人 IDE 配置（如果不想共享）
- [ ] `env.example` 文件已创建，且不包含真实密钥

## 💡 提交信息规范

建议使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` - 新功能
- `fix:` - 修复 bug
- `docs:` - 文档更新
- `style:` - 代码格式（不影响功能）
- `refactor:` - 重构
- `test:` - 测试相关
- `chore:` - 构建/工具相关

示例：
```
feat: 添加房间创建和Token生成API
fix: 修复环境变量验证问题
docs: 更新API文档
```

## 🚨 如果误提交了敏感文件

如果已经提交了包含敏感信息的文件：

```bash
# 1. 从 Git 历史中删除文件（但保留本地文件）
git rm --cached .env.local

# 2. 更新 .gitignore 确保文件被忽略
echo ".env.local" >> .gitignore

# 3. 提交更改
git add .gitignore
git commit -m "chore: 从版本控制中移除敏感文件"

# 4. 如果已经推送到远程，需要强制推送（谨慎使用）
# git push --force

# 5. 如果敏感信息已经泄露，立即更换所有密钥！
```

## 📚 更多资源

- [Git 最佳实践](https://git-scm.com/book)
- [.gitignore 模板](https://github.com/github/gitignore)
- [Conventional Commits](https://www.conventionalcommits.org/)

