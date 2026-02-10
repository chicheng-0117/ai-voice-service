# API Token 认证文档

## 概述

API 服务现在使用 JWT Token 进行认证。所有接口（除了登录和健康检查）都需要在请求头中携带有效的 Token。

## 认证流程

### 1. 登录获取 Token

**请求**
```http
POST /api/auth/login
Content-Type: application/json

{
  "user_id": "user123",
  "username": "张三"  // 可选
}
```

**响应**
```json
{
  "code": 200,
  "success": true,
  "msg": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2024-01-01T13:00:00",
    "user_id": "user123",
    "username": "张三"
  }
}
```

### 2. 使用 Token 访问接口

在请求头中添加 `Authorization` 字段：

```http
GET /api/agents
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3. 登出（撤销 Token）

**请求**
```http
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**响应**
```json
{
  "code": 200,
  "success": true,
  "msg": "登出成功",
  "data": null
}
```

## Token 特性

- **有效期**: 1 小时
- **格式**: JWT (JSON Web Token)
- **算法**: HS256
- **存储**: 内存中（生产环境建议使用 Redis）

## 需要认证的接口

以下接口都需要在请求头中携带有效的 Token：

- `GET /api/agents` - 列出Agent
- `POST /api/rooms` - 创建房间
- `GET /api/rooms/{room_name}` - 获取房间信息
- `DELETE /api/rooms/{room_name}` - 删除房间
- `POST /api/tokens` - 生成LiveKit Token

## 不需要认证的接口

- `GET /` - 根路径
- `GET /health` - 健康检查
- `POST /api/auth/login` - 登录
- `POST /api/auth/logout` - 登出（需要Token，但这是认证接口本身）

## 错误响应

### Token 缺失
```json
{
  "code": 401,
  "success": false,
  "msg": "Token不能为空",
  "data": null
}
```

### Token 无效或过期
```json
{
  "code": 401,
  "success": false,
  "msg": "Token无效或已过期",
  "data": null
}
```

### 认证格式错误
```json
{
  "code": 401,
  "success": false,
  "msg": "无效的认证格式，请使用: Bearer <token>",
  "data": null
}
```

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 登录获取Token
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"user_id": "user123", "username": "张三"}
)
login_data = login_response.json()
token = login_data["data"]["token"]

# 2. 使用Token访问接口
headers = {"Authorization": f"Bearer {token}"}

# 获取Agent列表
agents_response = requests.get(
    f"{BASE_URL}/api/agents",
    headers=headers
)
print(agents_response.json())

# 创建房间
room_response = requests.post(
    f"{BASE_URL}/api/rooms",
    headers=headers,
    json={"agent_name": "peppa"}
)
print(room_response.json())

# 3. 登出
logout_response = requests.post(
    f"{BASE_URL}/api/auth/logout",
    headers=headers
)
print(logout_response.json())
```

### JavaScript/TypeScript 示例

```typescript
const BASE_URL = "http://localhost:8000";

// 1. 登录获取Token
const loginResponse = await fetch(`${BASE_URL}/api/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ user_id: "user123", username: "张三" })
});
const loginData = await loginResponse.json();
const token = loginData.data.token;

// 2. 使用Token访问接口
const headers = {
  "Authorization": `Bearer ${token}`,
  "Content-Type": "application/json"
};

// 获取Agent列表
const agentsResponse = await fetch(`${BASE_URL}/api/agents`, { headers });
const agents = await agentsResponse.json();
console.log(agents);

// 创建房间
const roomResponse = await fetch(`${BASE_URL}/api/rooms`, {
  method: "POST",
  headers,
  body: JSON.stringify({ agent_name: "peppa" })
});
const room = await roomResponse.json();
console.log(room);

// 3. 登出
const logoutResponse = await fetch(`${BASE_URL}/api/auth/logout`, {
  method: "POST",
  headers
});
const logout = await logoutResponse.json();
console.log(logout);
```

### cURL 示例

```bash
# 1. 登录
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "username": "张三"}'

# 2. 使用Token访问接口（替换 YOUR_TOKEN）
curl -X GET "http://localhost:8000/api/agents" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 登出
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 配置

在 `.env.local` 文件中配置：

```env
# API Token 认证密钥（可选，不设置会自动生成）
# 生产环境请务必设置一个强密钥
API_TOKEN_SECRET=your-secret-key-here
```

## 安全建议

1. **使用 HTTPS**: 生产环境必须使用 HTTPS 传输 Token
2. **设置强密钥**: 在 `.env.local` 中设置 `API_TOKEN_SECRET`
3. **Token 存储**: 当前使用内存存储，生产环境建议使用 Redis
4. **Token 刷新**: 考虑实现 Token 刷新机制
5. **速率限制**: 对登录接口实施速率限制，防止暴力破解

## 注意事项

- Token 有效期为 1 小时，过期后需要重新登录
- Token 存储在内存中，服务重启后所有 Token 失效
- 登出会立即撤销 Token，无法再次使用
- 一个用户可以同时拥有多个有效的 Token（多次登录）

