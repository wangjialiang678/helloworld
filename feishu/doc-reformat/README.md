# 飞书文档一键排版插件

基于AI的飞书文档智能排版工具，可以自动优化文档格式，包括：
- 自动识别并转换为列表
- 添加高亮块突出重点内容
- 将结构化数据转换为表格
- 优化标题层级

## 项目结构

```
feishu-doc-formatter/
├── frontend/           # 前端插件代码 (React + TypeScript)
│   ├── src/
│   │   ├── components/ # React组件
│   │   ├── api/        # API调用
│   │   ├── types/      # TypeScript类型定义
│   │   └── utils/      # 工具函数
│   └── public/         # 静态资源
├── backend/            # 后端服务 (Python + FastAPI)
│   ├── app/
│   │   ├── main.py     # FastAPI主程序
│   │   ├── feishu.py   # 飞书API封装
│   │   ├── ai.py       # AI分析模块
│   │   └── formatter.py # 文档格式化逻辑
│   └── requirements.txt
├── scripts/            # 部署脚本
└── docs/               # 文档
```

## 技术栈

### 前端
- React 18
- TypeScript
- Ant Design
- Vite

### 后端
- Python 3.9+
- FastAPI
- 飞书SDK (larksuiteoapi)
- 通义千问API

### 部署
- 腾讯云函数 SCF (Serverless)
- 或阿里云函数计算

## 快速开始

### 1. 环境准备

#### 前端
```bash
cd frontend
npm install
npm run dev
```

#### 后端
```bash
cd backend
pip install -r requirements.txt
python -m app.main
```

### 2. 配置环境变量

在 `backend/.env` 文件中配置：
```env
# 飞书应用配置
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret

# 通义千问配置
QWEN_API_KEY=your_qwen_api_key

# 服务配置
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. 开发模式运行

```bash
# 启动后端
cd backend
python -m app.main

# 启动前端 (新终端)
cd frontend
npm run dev
```

### 4. 部署到云函数

```bash
# 部署到腾讯云
cd scripts
./deploy-scf.sh

# 或部署到阿里云
./deploy-fc.sh
```

## 功能特性

- ✅ 智能识别文档结构
- ✅ AI驱动的格式优化
- ✅ 实时预览优化效果
- ✅ 一键应用/撤销
- ✅ 支持30+种Block类型
- ✅ 批量处理优化

## 使用说明

### 在飞书文档中使用

1. 在飞书文档中输入 `/` 或点击 `+`
2. 选择 "AI一键排版" 插件
3. 等待AI分析文档（5-10秒）
4. 预览优化效果
5. 点击"应用排版"完成优化

### 配置选项

- 优化级别：保守/标准/激进
- 自定义规则：设置哪些内容需要优化
- 保留原始格式：部分内容保持不变

## 开发指南

详见 [开发文档](./docs/DEVELOPMENT.md)

## 部署指南

详见 [部署文档](./docs/DEPLOYMENT.md)

## License

MIT License
