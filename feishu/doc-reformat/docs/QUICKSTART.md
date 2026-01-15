# 快速开始指南

10分钟快速上手飞书文档一键排版插件开发！

## 前置要求检查

在开始之前,确保您已具备:

- [ ] 飞书企业账号(管理员权限)
- [ ] Python 3.9+
- [ ] Node.js 18+
- [ ] Git
- [ ] 通义千问API Key ([获取地址](https://dashscope.console.aliyun.com/))

## 第一步: 获取代码 (1分钟)

```bash
# 克隆项目
git clone <your-repo-url>
cd feishu-doc-formatter

# 查看项目结构
ls -la
```

## 第二步: 飞书开放平台配置 (5分钟)

### 2.1 创建应用

1. 访问 https://open.feishu.cn/
2. 点击"创建企业自建应用"
3. 填写应用名称: `AI文档一键排版`
4. 记录 **App ID** 和 **App Secret**

### 2.2 添加能力和权限

1. 添加应用能力 → 选择"文档小组件"
2. 申请权限:
   - `docx:document` ✅
   - `docx:document:readonly` ✅
3. 等待权限审批通过

📖 **详细步骤**: 查看 [飞书开放平台配置指南](./FEISHU_SETUP.md)

## 第三步: 配置环境 (3分钟)

### 3.1 后端环境

```bash
cd backend

# 创建虚拟环境
python3.9 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 配置环境变量
cp .env.example .env
```

编辑 `.env` 文件:
```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxx        # 替换为您的App ID
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxx     # 替换为您的App Secret
QWEN_API_KEY=sk-xxxxxxxxxxxxx          # 替换为您的通义千问API Key
DEBUG=true
```

### 3.2 前端环境

```bash
# 新开一个终端
cd frontend

# 安装依赖
npm install

# 配置API地址
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env.development
```

## 第四步: 启动服务 (1分钟)

### 4.1 启动后端

```bash
cd backend
source venv/bin/activate
python -m app.main
```

✅ 看到 `Uvicorn running on http://0.0.0.0:8000` 表示成功

### 4.2 启动前端 (新终端)

```bash
cd frontend
npm run dev
```

✅ 看到 `Local: http://localhost:3000` 表示成功

## 第五步: 测试功能 (3分钟)

### 5.1 测试后端API

```bash
# 健康检查
curl http://localhost:8000/health

# 预期响应:
{
  "code": 0,
  "message": "服务正常",
  "data": {"status": "healthy"}
}
```

### 5.2 测试前端界面

1. 浏览器打开: http://localhost:3000
2. 应该看到插件主界面
3. 如果看到加载中或错误,检查后端是否正常运行

### 5.3 在飞书文档中测试

1. 打开任意飞书文档
2. 点击右上角 `···` → "添加文档应用"
3. 搜索您的应用名称并添加
4. 在文档中输入 `/` → 选择您的插件
5. 测试分析和优化功能

## 第六步: 下一步计划

恭喜!您已经完成基础设置,现在可以:

### 开发阶段
- 📝 查看[开发指南](./DEVELOPMENT.md)了解代码结构
- 🔧 根据需求定制功能
- 🧪 编写测试用例

### 部署阶段
- 🚀 查看[部署文档](./DEPLOYMENT.md)选择部署方案
- ☁️ 推荐使用腾讯云函数SCF(最简单)
- 🐳 或使用Docker部署

### 发布阶段
- 📱 查看[飞书配置指南](./FEISHU_SETUP.md)完成发布配置
- ✍️ 准备应用材料和截图
- 🎯 提交应用审核

## 常见问题速查

### ❌ 后端启动失败

**问题**: `ModuleNotFoundError`
```bash
# 解决方案:
source venv/bin/activate  # 确保虚拟环境已激活
pip install -r requirements.txt  # 重新安装依赖
```

**问题**: `lark-oapi` 导入错误
```bash
# 解决方案:
pip uninstall lark-oapi
pip install lark-oapi==1.2.15
```

### ❌ 前端启动失败

**问题**: `npm install` 失败
```bash
# 解决方案:
rm -rf node_modules package-lock.json
npm install --registry=https://registry.npmmirror.com
```

**问题**: 端口被占用
```bash
# 修改端口:
# 编辑 vite.config.ts 中的 server.port
```

### ❌ 无法连接后端

**检查清单**:
1. 后端是否正常运行? → `curl http://localhost:8000/health`
2. CORS配置是否正确? → 检查`.env`中的`ALLOWED_ORIGINS`
3. 前端API地址是否正确? → 检查`.env.development`

### ❌ 飞书API调用失败

**问题**: 401 Unauthorized
```
原因: App ID或Secret错误
解决: 检查.env配置是否正确
```

**问题**: 403 Forbidden
```
原因: 权限未通过或未添加应用为文档协作者
解决:
1. 确认权限已审批通过
2. 在文档中添加应用为协作者
```

### ❌ AI分析失败

**问题**: 通义千问API调用失败
```
原因: API Key错误或余额不足
解决:
1. 检查QWEN_API_KEY是否正确
2. 访问控制台查看余额和配额
3. 检查网络连接
```

## 实用命令速查

```bash
# 后端
cd backend
source venv/bin/activate      # 激活虚拟环境
python -m app.main            # 启动服务
pytest tests/                 # 运行测试

# 前端
cd frontend
npm run dev                   # 开发模式
npm run build                 # 构建生产版本
npm run preview               # 预览构建结果

# 部署
./scripts/deploy-scf.sh       # 部署到腾讯云
./scripts/deploy-fc.sh        # 部署到阿里云

# Git
git status                    # 查看状态
git add .                     # 添加所有更改
git commit -m "message"       # 提交
git push                      # 推送
```

## 开发工具推荐

- **IDE**: VS Code (推荐插件: Python, ESLint, Prettier)
- **API测试**: Postman 或 Insomnia
- **Git客户端**: GitKraken 或 SourceTree
- **数据库**: (如果需要) PostgreSQL + pgAdmin
- **监控**: (生产环境) Sentry, DataDog

## 学习资源

### 官方文档
- [飞书开放平台](https://open.feishu.cn/document/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [通义千问](https://help.aliyun.com/document_detail/2712195.html)

### 社区资源
- GitHub Issues: 提问和反馈
- 飞书开发者社区: 经验分享
- Stack Overflow: 技术问题

## 获取帮助

遇到问题?
1. 📖 首先查看相关文档
2. 🔍 搜索GitHub Issues
3. 💬 在开发者社区提问
4. 📧 联系技术支持

## 里程碑检查清单

完成以下检查点,确保一切就绪:

### 开发环境 ✅
- [ ] Python环境安装完成
- [ ] Node.js环境安装完成
- [ ] 依赖包安装成功
- [ ] 环境变量配置正确

### 本地测试 ✅
- [ ] 后端API正常响应
- [ ] 前端界面正常显示
- [ ] 飞书API调用成功
- [ ] AI分析功能正常

### 飞书配置 ✅
- [ ] 应用创建完成
- [ ] 权限申请通过
- [ ] 文档小组件配置完成
- [ ] 在文档中成功调用插件

### 功能验证 ✅
- [ ] 文档分析功能正常
- [ ] 优化建议准确
- [ ] 预览显示正确
- [ ] 应用优化成功

### 准备部署 ✅
- [ ] 选择部署方案
- [ ] 准备服务器/云函数
- [ ] 配置域名和SSL
- [ ] 准备发布材料

---

🎉 **恭喜!** 您已完成所有基础配置!

现在可以开始定制开发或直接部署上线了。

**下一步建议**:
1. 本地测试核心功能
2. 根据需求定制优化
3. 选择部署方案并上线
4. 提交飞书应用审核

祝开发顺利! 🚀
