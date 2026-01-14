# 开发指南

本文档说明如何进行本地开发和调试。

## 开发环境要求

### 系统要求
- **操作系统**: macOS / Linux / Windows (WSL)
- **Node.js**: 18.x 或更高
- **Python**: 3.9 或更高
- **npm**: 9.x 或更高

### 必备工具
- Git
- VS Code (推荐) 或其他IDE
- Postman 或 curl (API测试)

## 环境搭建

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd feishu-doc-formatter
```

### 2. 后端环境

```bash
cd backend

# 创建虚拟环境
python3.9 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 配置环境变量
cp .env.example .env
vi .env  # 填写实际配置
```

`.env` 配置示例:
```env
FEISHU_APP_ID=cli_a1b2c3d4e5f6g7h8
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. 前端环境

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env.development
```

## 本地运行

### 1. 启动后端

```bash
cd backend
source venv/bin/activate
python -m app.main
```

后端将运行在: `http://localhost:8000`

API文档: `http://localhost:8000/docs`

### 2. 启动前端

```bash
# 新开一个终端
cd frontend
npm run dev
```

前端将运行在: `http://localhost:3000`

## 项目结构详解

```
feishu-doc-formatter/
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── components/       # React组件
│   │   │   └── FormatterPanel.tsx  # 主界面组件
│   │   ├── api/              # API调用
│   │   │   └── index.ts      # API方法封装
│   │   ├── types/            # TypeScript类型
│   │   │   └── index.ts      # 类型定义
│   │   ├── App.tsx           # 主应用组件
│   │   ├── main.tsx          # 入口文件
│   │   └── index.css         # 样式
│   ├── package.json          # 前端依赖
│   ├── tsconfig.json         # TS配置
│   ├── vite.config.ts        # Vite配置
│   └── index.html            # HTML模板
├── backend/                  # 后端代码
│   ├── app/
│   │   ├── main.py           # FastAPI主程序
│   │   ├── config.py         # 配置管理
│   │   ├── feishu.py         # 飞书API封装
│   │   ├── ai.py             # AI分析模块
│   │   └── __init__.py
│   ├── requirements.txt      # Python依赖
│   ├── Dockerfile            # Docker配置
│   └── .env.example          # 环境变量示例
├── scripts/                  # 部署脚本
│   ├── deploy-scf.sh         # 腾讯云函数部署
│   └── deploy-fc.sh          # 阿里云函数部署
├── docs/                     # 文档
│   ├── DEVELOPMENT.md        # 开发指南
│   └── DEPLOYMENT.md         # 部署文档
└── README.md                 # 项目说明
```

## 核心模块说明

### 前端核心组件

#### FormatterPanel.tsx
主界面组件，包含:
- 文档分析状态显示
- 优化建议列表
- 预览对比
- 应用/取消操作

关键方法:
- `handleAnalyze()`: 触发文档分析
- `handleApply()`: 应用优化建议
- `renderSuggestion()`: 渲染单个建议

#### API封装 (api/index.ts)
API方法:
- `analyze()`: 分析文档
- `applyOptimization()`: 应用优化
- `getDocumentInfo()`: 获取文档信息

### 后端核心模块

#### main.py
FastAPI主程序，包含:
- API路由定义
- 请求处理
- 错误处理
- CORS配置

主要端点:
- `POST /api/analyze`: 分析文档
- `POST /api/apply`: 应用优化
- `GET /api/document/{id}`: 获取文档信息

#### feishu.py
飞书API封装，包含:
- 文档Block获取
- Block批量更新
- Block创建/删除
- 认证管理

关键方法:
- `get_document_blocks()`: 获取所有Block
- `batch_update_blocks()`: 批量更新
- `create_block()`: 创建Block
- `delete_block()`: 删除Block

#### ai.py
AI分析模块，包含:
- 通义千问API调用
- 提示词构建
- 响应解析
- 降级策略

关键方法:
- `analyze_document()`: 主分析方法
- `_build_prompt()`: 构建提示词
- `_parse_ai_response()`: 解析AI响应
- `_get_fallback_analysis()`: 降级分析

## 开发流程

### 添加新的Block类型支持

1. **更新类型定义** (`frontend/src/types/index.ts`):
```typescript
export enum BlockType {
  // ... 现有类型
  NewType = 99,  // 添加新类型
}
```

2. **更新AI分析逻辑** (`backend/app/ai.py`):
```python
def _build_prompt(self, blocks, config):
    # 在提示词中添加新类型的说明
    prompt = f"""
    ...
    5. 转换为XXX (newtype=99): 适用于...
    ...
    """
```

3. **更新Block更新逻辑** (`backend/app/feishu.py`):
```python
async def _update_batch(self, document_id, batch):
    for block_update in batch:
        if block_update["block_type"] == 99:
            # 处理新类型的更新逻辑
            pass
```

4. **更新前端显示** (`frontend/src/components/FormatterPanel.tsx`):
```typescript
const blockTypeNames: Record<number, string> = {
  // ... 现有映射
  [BlockType.NewType]: 'XXX类型',
};
```

### 调试技巧

#### 后端调试

使用VS Code调试配置 (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "app.main",
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "DEBUG": "true"
      }
    }
  ]
}
```

在代码中添加断点，按F5启动调试。

#### 前端调试

在浏览器中使用DevTools:
- 打开控制台查看日志
- 使用Network标签查看API请求
- 使用React DevTools查看组件状态

#### API调试

使用curl测试API:
```bash
# 健康检查
curl http://localhost:8000/health

# 分析文档
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"document_id": "test_doc_id", "config": {}}'
```

或使用Postman导入API集合。

## 测试

### 单元测试

```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
npm test
```

### 集成测试

```bash
# 启动后端
cd backend && python -m app.main &

# 运行集成测试
cd tests && python test_integration.py
```

## 代码规范

### Python (后端)
- 遵循PEP 8规范
- 使用type hints
- 添加docstring

```python
async def get_document_blocks(self, document_id: str) -> List[Dict[str, Any]]:
    """
    获取文档所有Block

    Args:
        document_id: 文档ID

    Returns:
        Block列表
    """
    pass
```

### TypeScript (前端)
- 使用ESLint
- 明确类型声明
- 添加注释

```typescript
/**
 * 分析文档
 * @param documentId 文档ID
 * @param config 配置选项
 * @returns 分析结果
 */
async function analyze(
  documentId: string,
  config: FormatterConfig
): Promise<AnalysisResult>
```

## 性能优化

### 前端优化
- 使用React.memo减少重渲染
- 懒加载组件
- 优化API调用频率

### 后端优化
- 使用异步IO
- 添加缓存机制
- 批量处理请求

## 常见问题

### Q: 后端启动报错"模块找不到"?
**A**: 确保虚拟环境已激活，依赖已安装

### Q: 前端无法连接后端?
**A**: 检查:
1. 后端是否正常运行
2. CORS配置是否正确
3. API地址是否正确

### Q: AI分析很慢?
**A**:
- 检查网络连接
- 考虑增加超时时间
- 使用更快的AI模型

### Q: 飞书API调用失败?
**A**:
- 检查App ID和Secret是否正确
- 确认应用权限已申请
- 查看飞书API文档确认参数

## Git工作流

### 分支管理
- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: 修复分支

### 提交规范
```
type(scope): subject

body

footer
```

类型:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档
- `style`: 格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例:
```
feat(ai): add support for table conversion

- Add table detection in AI analyzer
- Implement table block creation
- Update prompt template

Closes #123
```

## 下一步

开发完成后:
1. 编写单元测试
2. 进行代码审查
3. 更新文档
4. 提交部署

## 参考资源

- [飞书开放平台文档](https://open.feishu.cn/document/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [React文档](https://react.dev/)
- [通义千问文档](https://help.aliyun.com/document_detail/2712195.html)
