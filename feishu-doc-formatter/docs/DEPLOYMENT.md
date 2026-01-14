# 部署文档

本文档详细说明如何将飞书文档一键排版插件部署到生产环境。

## 部署方案对比

| 方案 | 难度 | 成本/月 | 性能 | 推荐度 |
|------|------|---------|------|--------|
| 腾讯云函数 SCF | ⭐⭐ | 50-200元 | 良好 | ⭐⭐⭐⭐⭐ |
| 阿里云函数计算 FC | ⭐⭐ | 50-200元 | 良好 | ⭐⭐⭐⭐ |
| 云服务器 | ⭐⭐⭐⭐ | 200-400元 | 优秀 | ⭐⭐⭐ |
| Docker容器 | ⭐⭐⭐ | 150-300元 | 优秀 | ⭐⭐⭐⭐ |

**推荐**: 对于初期使用，推荐使用**腾讯云函数SCF**，最简单且成本最低。

## 方案一：腾讯云函数 SCF (推荐)

### 1. 准备工作

#### 1.1 注册腾讯云账号
访问 [腾讯云](https://cloud.tencent.com/) 注册账号并完成实名认证

#### 1.2 开通云函数服务
- 登录腾讯云控制台
- 搜索"云函数 SCF"
- 开通服务（有免费额度）

#### 1.3 安装部署工具
```bash
# 安装腾讯云CLI
pip install scf-cli

# 配置认证信息
scf configure set --secret-id <your-secret-id> --secret-key <your-secret-key> --region ap-guangzhou
```

### 2. 部署步骤

#### 2.1 配置环境变量
```bash
# 设置环境变量
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export QWEN_API_KEY="your_qwen_api_key"
```

#### 2.2 执行部署
```bash
cd feishu-doc-formatter
./scripts/deploy-scf.sh
```

#### 2.3 配置API网关
1. 登录腾讯云控制台 → 云函数
2. 找到 `feishu-doc-formatter` 函数
3. 点击"触发管理" → "创建触发器"
4. 选择"API网关触发器"
5. 配置:
   - 启用集成响应: 是
   - 请求方法: ANY
   - 发布环境: release
6. 保存后获得API网关地址，如: `https://service-xxx.gz.apigw.tencentcs.com/release/`

### 3. 验证部署
```bash
# 健康检查
curl https://your-api-gateway-url/health

# 预期响应
{
  "code": 0,
  "message": "服务正常",
  "data": {
    "status": "healthy"
  }
}
```

### 4. 更新代码
```bash
# 修改代码后重新部署
./scripts/deploy-scf.sh
```

## 方案二：阿里云函数计算 FC

### 1. 准备工作

#### 1.1 注册阿里云账号
访问 [阿里云](https://www.aliyun.com/) 注册账号并完成实名认证

#### 1.2 开通函数计算服务
- 登录阿里云控制台
- 搜索"函数计算"
- 开通服务

#### 1.3 安装部署工具
```bash
# 安装Fun工具
npm install -g @alicloud/fun

# 配置认证信息
fun config
```

### 2. 部署步骤

```bash
# 设置环境变量
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export QWEN_API_KEY="your_qwen_api_key"

# 执行部署
cd feishu-doc-formatter
./scripts/deploy-fc.sh
```

### 3. 获取访问地址
部署完成后，控制台会显示HTTP触发器地址

## 方案三：云服务器部署

### 1. 准备云服务器

推荐配置:
- **CPU**: 2核
- **内存**: 4GB
- **带宽**: 3Mbps
- **系统**: Ubuntu 20.04 LTS

### 2. 安装环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.9
sudo apt install python3.9 python3.9-venv python3-pip -y

# 安装Node.js (前端构建需要)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装Nginx
sudo apt install nginx -y
```

### 3. 部署后端

```bash
# 创建应用目录
mkdir -p /opt/feishu-formatter
cd /opt/feishu-formatter

# 复制代码 (使用git或scp)
git clone <your-repo-url> .

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 配置环境变量
cp .env.example .env
vi .env  # 填写实际配置

# 测试运行
python -m app.main
```

### 4. 配置系统服务

创建systemd服务文件 `/etc/systemd/system/feishu-formatter.service`:

```ini
[Unit]
Description=Feishu Doc Formatter API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/feishu-formatter/backend
Environment="PATH=/opt/feishu-formatter/venv/bin"
ExecStart=/opt/feishu-formatter/venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable feishu-formatter
sudo systemctl start feishu-formatter
sudo systemctl status feishu-formatter
```

### 5. 配置Nginx反向代理

创建Nginx配置 `/etc/nginx/sites-available/feishu-formatter`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置:
```bash
sudo ln -s /etc/nginx/sites-available/feishu-formatter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. 配置HTTPS (可选但推荐)

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 方案四：Docker部署

### 1. 安装Docker

```bash
# 安装Docker
curl -fsSL https://get.docker.com | bash -s docker

# 安装Docker Compose
sudo apt install docker-compose -y
```

### 2. 构建镜像

```bash
cd feishu-doc-formatter/backend
docker build -t feishu-formatter:latest .
```

### 3. 运行容器

```bash
docker run -d \
  --name feishu-formatter \
  -p 8000:8000 \
  -e FEISHU_APP_ID="your_app_id" \
  -e FEISHU_APP_SECRET="your_app_secret" \
  -e QWEN_API_KEY="your_qwen_api_key" \
  --restart unless-stopped \
  feishu-formatter:latest
```

### 4. 使用Docker Compose

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - FEISHU_APP_ID=${FEISHU_APP_ID}
      - FEISHU_APP_SECRET=${FEISHU_APP_SECRET}
      - QWEN_API_KEY=${QWEN_API_KEY}
    restart: unless-stopped
```

启动:
```bash
docker-compose up -d
```

## 前端部署

### 1. 构建前端

```bash
cd feishu-doc-formatter/frontend

# 安装依赖
npm install

# 配置API地址
echo "VITE_API_BASE_URL=https://your-api-url" > .env.production

# 构建
npm run build
```

### 2. 部署静态文件

**方案A: 使用对象存储 (推荐)**
```bash
# 上传到腾讯云COS或阿里云OSS
# 配置静态网站托管
# 绑定自定义域名
```

**方案B: 使用Nginx**
```bash
# 复制构建产物
sudo cp -r dist/* /var/www/html/feishu-formatter/
```

## 监控和日志

### 云函数日志查看
- 腾讯云: 控制台 → 云函数 → 日志查询
- 阿里云: 控制台 → 函数计算 → 日志服务

### 云服务器日志查看
```bash
# 查看服务日志
sudo journalctl -u feishu-formatter -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 常见问题

### Q1: 部署后无法访问?
**A**: 检查安全组/防火墙规则，确保开放了相应端口

### Q2: 云函数超时?
**A**: 增加函数超时时间(最大900秒)，或优化AI调用速度

### Q3: 成本过高?
**A**:
- 使用云函数按需计费
- 优化AI调用次数
- 启用缓存机制

### Q4: 如何回滚版本?
**A**:
- 云函数: 使用版本管理功能
- 云服务器: 使用git回退代码

## 下一步

部署完成后:
1. 在飞书开放平台配置插件的后端地址
2. 测试完整功能流程
3. 提交应用审核
4. 发布到飞书应用中心

## 技术支持

遇到问题请查看:
- [飞书开放平台文档](https://open.feishu.cn/)
- [腾讯云函数文档](https://cloud.tencent.com/document/product/583)
- [阿里云函数计算文档](https://help.aliyun.com/product/50980.html)
