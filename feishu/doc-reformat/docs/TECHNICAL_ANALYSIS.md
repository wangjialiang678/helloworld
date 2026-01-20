# 飞书文档一键排版项目 - 技术分析与方案选择

## 目录
- [项目背景](#项目背景)
- [需求分析](#需求分析)
- [飞书开放平台技术架构](#飞书开放平台技术架构)
- [技术方案调研](#技术方案调研)
- [方案对比分析](#方案对比分析)
- [最终方案](#最终方案)
- [技术实现细节](#技术实现细节)

---

## 项目背景

### 核心需求
创建一个飞书文档小组件（文档插件），实现**一键智能排版**功能：
- 自动美化混乱的文档格式
- 保持内容不变，仅优化结构
- 智能识别并转换为合适的格式：列表、表格、思维导图、高亮块等
- 优化标题层级结构

### 研究方向
1. 飞书文档格式和Block架构
2. API权限和调用方式
3. 部署方式和架构选择

---

## 需求分析

### 功能需求
1. **智能分析**：AI识别文档内容结构和语义
2. **格式优化建议**：提供多种优化方案供用户选择
3. **实时预览**：优化前后对比效果
4. **一键应用**：批量更新文档格式
5. **可配置**：支持自定义优化规则和级别

### 非功能需求
1. **响应速度**：分析 + 应用 ≤ 10秒（正常文档）
2. **准确性**：AI识别准确率 ≥ 85%
3. **安全性**：不能泄露API密钥，保护用户文档隐私
4. **易用性**：无需复杂配置，开箱即用

---

## 飞书开放平台技术架构

### 1. 飞书文档 Block 架构

飞书文档基于 **Block 体系**构建，每个 Block 代表一个独立的内容单元：

#### Block 类型（30+ 种）
| 类型 | ID | 说明 | 应用场景 |
|------|-----|------|----------|
| Page | 1 | 页面 | 文档根节点 |
| Text | 2 | 文本段落 | 普通段落 |
| Heading1-9 | 3-11 | 标题 | 文档结构层级 |
| Bullet | 12 | 无序列表 | 项目列表、要点 |
| Ordered | 13 | 有序列表 | 步骤、排名 |
| Code | 14 | 代码块 | 代码展示 |
| Quote | 15 | 引用块 | 引用内容 |
| Todo | 17 | 待办事项 | 任务清单 |
| Bitable | 18 | 多维表格 | 结构化数据 |
| Callout | 19 | 高亮块 | 重点提示 |
| Table | 31 | 表格 | 数据展示 |
| Divider | 22 | 分隔线 | 内容分隔 |
| File | 23 | 文件 | 附件 |
| Grid | 24 | 分栏 | 多栏布局 |

**Block 层级关系**：
- 文档采用树形结构
- 每个 Block 可以包含子 Block（children）
- 父子关系通过 `parent_id` 和 `children[]` 维护

### 2. 飞书小组件（文档插件）架构

#### 小组件类型
飞书支持两类小组件：
1. **iframe 小组件**：独立 URL，完整前端应用
2. **block 小组件**：基于飞书 Block SDK，轻量级

本项目采用 **iframe 小组件**，原因：
- 需要复杂 UI 交互（优化预览、配置面板）
- 需要与后端服务通信
- 更高的自定义自由度

#### 小组件开发流程
```
1. 飞书开放平台创建应用
   ↓
2. 配置小组件信息（名称、描述、URL）
   ↓
3. 开发前端界面（React/Vue）
   ↓
4. 使用 Block API 读取/修改文档
   ↓
5. 打包上传（opdev CLI 或手动上传）
   ↓
6. CDN 托管分发（飞书自动）
   ↓
7. 用户在文档中插入使用
```

### 3. API 架构：Client API vs Server API

飞书提供两套 API 体系：

#### Server API
- **运行环境**：服务器后端
- **认证方式**：tenant_access_token（应用身份）
- **权限范围**：全局，可访问所有授权资源
- **使用场景**：批量操作、敏感操作、定时任务
- **安全性**：App Secret 保存在服务器

#### Client API
- **运行环境**：浏览器前端（iframe 内）
- **认证方式**：tt.requestAuthCode 获取临时授权
- **权限范围**：当前文档，仅可操作用户打开的文档
- **使用场景**：小组件内读取/修改当前文档
- **安全性**：无需暴露 App Secret

**Client API 能力**：
```javascript
// 获取文档内容
tt.getDocumentBlocks({
  document_id: 'xxx'
})

// 批量更新 Block
tt.updateDocumentBlocks({
  document_id: 'xxx',
  requests: [
    { block_id: 'xxx', block_type: 12 } // 转为列表
  ]
})

// 插入新 Block
tt.insertBlocks({...})

// 删除 Block
tt.deleteBlocks({...})
```

### 4. 部署架构

飞书小组件的前端代码具有以下特点：
- **CDN 托管**：上传后由飞书 CDN 自动分发
- **全球加速**：飞书基础设施提供高速访问
- **免运维**：无需维护静态服务器
- **自动 HTTPS**：飞书统一提供 SSL 证书

---

## 技术方案调研

### 方案探索过程

#### 阶段 1：初始方案（全栈架构）
**假设**：小组件需要完整的前后端服务

**架构**：
```
前端（React） ←→ 后端服务（FastAPI + Qwen AI） ←→ 飞书 API
     ↓
云服务器部署（阿里云/腾讯云）
```

**问题**：
- 需要维护服务器
- 部署和运维成本较高
- 用户需要自行部署后端服务

#### 阶段 2：纯前端方案探索
**灵感来源**：飞书官方文档提到
> "对于您期望的一键排版功能，所有计算和操作都可以在用户本地的浏览器环境中完成。小组件的前端代码在上传后，会由飞书的CDN进行托管和分发。因此，本项目无需您额外部署或维护任何服务器"

**理想架构**：
```
前端（React）
  ↓ Client API
飞书文档
  ↓ CDN 托管
用户浏览器
```

**深入调研发现的问题**：

1. **AI 分析必须调用外部 API**
   - 本地浏览器无法运行大模型
   - 必须调用通义千问/GPT 等云端 API

2. **API 密钥安全问题**
   ```javascript
   // ❌ 前端代码暴露 API Key（严重安全问题）
   const API_KEY = "sk-xxxxx" // 任何人都能看到！

   fetch('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation', {
     headers: {
       'Authorization': `Bearer ${API_KEY}`
     }
   })
   ```

   **风险**：
   - API Key 会暴露在前端代码中
   - 用户可以通过浏览器开发者工具查看
   - 恶意用户可以盗用 Key，产生巨额费用
   - 无法控制调用频率和额度

3. **跨域问题**
   - 飞书小组件在 iframe 中运行
   - 直接调用第三方 API 会遇到 CORS 限制

**结论**：纯前端方案在安全性上存在致命缺陷，不可行。

#### 阶段 3：混合架构（最终方案）
**架构设计**：
```
前端（飞书 CDN 托管）
  ↓ Client API（读写文档）
飞书文档
  ↓ HTTPS
轻量级后端（Serverless 云函数）
  ↓ 安全存储 API Key
AI 服务（通义千问）
```

**优势**：
- ✅ 前端无需部署：飞书 CDN 自动托管
- ✅ 后端轻量化：仅用于 AI 调用代理
- ✅ 安全可靠：API Key 不暴露
- ✅ 按量计费：Serverless 成本极低
- ✅ 自动扩缩容：无需关心并发

---

## 方案对比分析

### 方案对比表

| 对比项 | 纯前端方案 | 传统全栈方案 | Serverless 混合方案 ✅ |
|--------|-----------|-------------|---------------------|
| **部署复杂度** | ⭐⭐⭐⭐⭐ 仅前端 | ⭐⭐ 需部署前后端 | ⭐⭐⭐⭐ 前端自动托管 |
| **运维成本** | ⭐⭐⭐⭐⭐ 零运维 | ⭐⭐ 需维护服务器 | ⭐⭐⭐⭐ 函数自动运维 |
| **安全性** | ⭐ API Key 暴露 | ⭐⭐⭐⭐⭐ 完全安全 | ⭐⭐⭐⭐⭐ 完全安全 |
| **性能** | ⭐⭐⭐⭐ 快速响应 | ⭐⭐⭐ 取决于服务器 | ⭐⭐⭐⭐ 全球加速 |
| **成本** | ⭐⭐⭐⭐⭐ 零成本 | ⭐⭐ 固定服务器成本 | ⭐⭐⭐⭐ 按调用计费 |
| **扩展性** | ⭐⭐ 受浏览器限制 | ⭐⭐⭐ 手动扩容 | ⭐⭐⭐⭐⭐ 自动扩缩容 |
| **开发复杂度** | ⭐⭐⭐⭐ 简单 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐ 较简单 |

### 详细分析

#### 纯前端方案
**优势**：
- 部署极简：仅需上传前端代码到飞书
- 零运维成本
- 响应速度快

**劣势**：
- ❌ **致命缺陷**：API Key 必然暴露，存在严重安全风险
- ❌ 无法调用需要密钥的外部服务
- ❌ 跨域限制

**适用场景**：
- 纯静态展示
- 不需要调用外部 API
- 所有计算可在浏览器完成

#### 传统全栈方案
**优势**：
- 完全控制：服务器环境完全可控
- 功能完整：可实现复杂业务逻辑
- 安全性高：密钥安全存储

**劣势**：
- 部署复杂：需要购买/配置服务器
- 运维成本高：监控、升级、备份
- 固定成本：即使无人使用也需付费
- 扩容困难：需要手动配置负载均衡

**适用场景**：
- 企业级应用
- 需要复杂状态管理
- 高并发高可用需求

#### Serverless 混合方案 ⭐
**优势**：
- ✅ 部署简单：前端 CDN 托管 + 云函数部署
- ✅ 运维极简：云平台自动管理
- ✅ 安全可靠：API Key 在云函数中安全存储
- ✅ 按量计费：无请求零成本，有请求按次计费
- ✅ 自动扩容：云平台自动处理并发
- ✅ 全球加速：CDN + 多区域函数部署

**劣势**：
- 冷启动延迟：首次调用可能需要 1-2 秒（可通过预热缓解）
- 平台依赖：依赖云厂商（但可多云部署）

**适用场景**：
- ✅ 本项目：前端简单 + AI 分析代理
- ✅ 轻量级应用
- ✅ 不确定流量规模的项目

---

## 最终方案

### 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │            飞书文档 (iframe 小组件)              │   │
│  │                                                  │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │  前端应用 (React + TypeScript)          │  │   │
│  │  │  - FormatterPanel 组件                   │  │   │
│  │  │  - 优化预览界面                          │  │   │
│  │  │  - Client API 调用                       │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  │                      ↓ Client API              │   │
│  │  ┌──────────────────────────────────────────┐  │   │
│  │  │      飞书文档 Block 内容                 │  │   │
│  │  │  - 读取文档结构                          │  │   │
│  │  │  - 批量更新 Block                        │  │   │
│  │  └──────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────┬─────────────────────────────────────────┘
                │ HTTPS
                ↓
┌─────────────────────────────────────────────────────────┐
│              飞书 CDN（自动托管前端代码）                │
│  - 全球加速节点                                          │
│  - 自动 HTTPS                                            │
│  - 零配置运维                                            │
└─────────────────────────────────────────────────────────┘

                ↓ HTTPS (AI 分析请求)

┌─────────────────────────────────────────────────────────┐
│        Serverless 云函数（腾讯 SCF / 阿里 FC）          │
│  ┌─────────────────────────────────────────────────┐   │
│  │    FastAPI 后端服务                             │   │
│  │    - AI 分析 API (/api/analyze)                 │   │
│  │    - 接收文档 Block 数据                        │   │
│  │    - 调用 AI 生成优化建议                       │   │
│  │    - 返回优化方案                               │   │
│  └─────────────────┬───────────────────────────────┘   │
│                    │                                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │  环境变量（安全存储）                           │   │
│  │  - QWEN_API_KEY: AI 服务密钥                    │   │
│  │  - FEISHU_APP_ID/SECRET: 飞书应用凭证          │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────┬─────────────────────────────────────────┘
                │ HTTPS
                ↓
┌─────────────────────────────────────────────────────────┐
│           通义千问 API（阿里云 DashScope）              │
│  - 接收文档结构分析请求                                  │
│  - 返回格式优化建议                                      │
│  - 提供置信度评分                                        │
└─────────────────────────────────────────────────────────┘
```

### 技术栈选择

#### 前端
- **React 18**：组件化开发，生态成熟
- **TypeScript**：类型安全，提升代码质量
- **Ant Design**：飞书风格接近，组件丰富
- **Vite**：快速构建，开发体验好

**为什么选择 React？**
- 飞书 Block SDK 提供 React 示例
- 社区资源丰富，问题容易解决
- 组件化适合复杂 UI 交互

#### 后端
- **Python 3.9+**：AI 生态最成熟
- **FastAPI**：高性能，异步支持，自动生成文档
- **通义千问 API**：中文理解能力强，性价比高

**为什么选择 FastAPI？**
- 原生异步：高并发性能好
- 自动校验：Pydantic 模型自动验证请求
- OpenAPI 文档：自动生成接口文档
- Serverless 友好：启动快，内存占用小

**为什么选择通义千问？**
- 中文优化：飞书文档主要是中文
- 价格优势：比 GPT-4 便宜 80%
- 响应速度快：国内网络延迟低
- 上下文长度：支持 8K tokens，足够分析长文档

#### 部署
**云函数平台**：
- **腾讯云 SCF**：与微信生态集成好
- **阿里云 FC**：与通义千问同厂商，网络快

**为什么选择 Serverless？**
- 零运维：无需管理服务器
- 按量计费：10000 次调用约 ¥1
- 自动扩容：应对流量突增
- 快速部署：一键发布更新

---

## 技术实现细节

### 1. 前端架构

#### 核心组件
```typescript
// FormatterPanel.tsx - 主界面组件
interface FormatterPanelProps {
  documentId: string;  // 当前文档 ID
}

interface OptimizationSuggestion {
  block_id: string;           // Block ID
  original_type: BlockType;   // 原始类型
  suggested_type: BlockType;  // 建议类型
  reason: string;             // 优化原因
  confidence: number;         // 置信度 0-1
  preview?: {                 // 预览
    before: string;
    after: string;
  };
}

export const FormatterPanel: React.FC<FormatterPanelProps> = ({ documentId }) => {
  // 状态管理
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);

  // 分析文档
  const handleAnalyze = async () => {
    setLoading(true);

    // 1. 读取文档 Block（使用 Client API）
    const blocks = await tt.getDocumentBlocks({ document_id: documentId });

    // 2. 调用后端 AI 分析
    const response = await fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      body: JSON.stringify({ document_id: documentId, blocks })
    });

    const result = await response.json();
    setSuggestions(result.data.suggestions);
    setLoading(false);
  };

  // 应用优化
  const handleApply = async () => {
    // 批量更新 Block（使用 Client API）
    await tt.updateDocumentBlocks({
      document_id: documentId,
      requests: suggestions.map(s => ({
        block_id: s.block_id,
        block_type: s.suggested_type
      }))
    });
  };

  return (
    <div className="formatter-panel">
      <Button onClick={handleAnalyze} loading={loading}>
        分析文档
      </Button>

      {suggestions.length > 0 && (
        <>
          <SuggestionList suggestions={suggestions} />
          <Button onClick={handleApply}>应用优化</Button>
        </>
      )}
    </div>
  );
};
```

#### Client API 封装
```typescript
// api/feishu.ts
export const FeishuAPI = {
  // 获取文档所有 Block
  async getDocumentBlocks(documentId: string): Promise<Block[]> {
    return new Promise((resolve, reject) => {
      tt.getDocumentBlocks({
        document_id: documentId,
        success: (res) => resolve(res.blocks),
        fail: (err) => reject(err)
      });
    });
  },

  // 批量更新 Block
  async updateBlocks(documentId: string, updates: BlockUpdate[]) {
    return new Promise((resolve, reject) => {
      tt.updateDocumentBlocks({
        document_id: documentId,
        requests: updates,
        success: resolve,
        fail: reject
      });
    });
  }
};
```

### 2. 后端架构

#### API 端点设计
```python
# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="飞书文档智能排版 API")

class AnalyzeRequest(BaseModel):
    document_id: str
    blocks: List[Dict]
    config: Optional[Dict] = None

class AnalyzeResponse(BaseModel):
    code: int
    message: str
    data: Dict[str, Any]

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_document(request: AnalyzeRequest):
    """分析文档并返回优化建议"""

    # 1. 调用 AI 分析
    analyzer = AIAnalyzer()
    suggestions = await analyzer.analyze_document(
        blocks=request.blocks,
        config=request.config
    )

    # 2. 返回结果
    return AnalyzeResponse(
        code=0,
        message="分析成功",
        data={
            "suggestions": suggestions,
            "total_blocks": len(request.blocks),
            "optimizable_blocks": len(suggestions)
        }
    )
```

#### AI 分析模块
```python
# app/ai.py
from dashscope import Generation

class AIAnalyzer:
    def __init__(self):
        self.model = "qwen-plus"
        self.api_key = os.getenv("QWEN_API_KEY")

    async def analyze_document(self, blocks: List[Dict], config: Dict) -> List[Dict]:
        """使用 AI 分析文档结构"""

        # 1. 构建 prompt
        prompt = self._build_prompt(blocks, config)

        # 2. 调用通义千问 API
        response = Generation.call(
            model=self.model,
            api_key=self.api_key,
            prompt=prompt,
            result_format='message'
        )

        # 3. 解析 AI 返回的建议
        suggestions = self._parse_response(response.output.text)

        return suggestions

    def _build_prompt(self, blocks: List[Dict], config: Dict) -> str:
        """构建 AI 分析 prompt"""
        return f"""
你是一个文档格式优化专家。请分析以下飞书文档内容，给出格式优化建议。

文档结构：
{json.dumps(blocks, ensure_ascii=False, indent=2)}

优化规则：
1. 连续的短句（< 15字）→ 无序列表（Bullet）
2. 有明显顺序/步骤的内容 → 有序列表（Ordered）
3. 重要提示/警告 → 高亮块（Callout）
4. 结构化数据（3列以上）→ 表格（Table）
5. 无格式的标题文本 → 对应层级的标题（Heading）

请返回 JSON 格式的优化建议，格式如下：
[
  {{
    "block_id": "块ID",
    "original_type": 2,
    "suggested_type": 12,
    "reason": "连续的短句，适合转为列表",
    "confidence": 0.85
  }}
]

注意：
- 只建议必要的优化，不要过度优化
- confidence 表示置信度（0-1），低于 0.7 的不要返回
- 保持文档的整体风格一致
"""

    def _parse_response(self, text: str) -> List[Dict]:
        """解析 AI 返回的 JSON"""
        try:
            # 提取 JSON 部分（AI 可能返回额外说明文字）
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"解析 AI 响应失败: {e}")
            return []
```

### 3. 部署配置

#### 云函数配置（腾讯云 SCF）
```yaml
# serverless.yml
service: feishu-formatter

provider:
  name: tencent
  runtime: Python3.9
  region: ap-guangzhou
  memorySize: 512
  timeout: 30

functions:
  api:
    handler: app.main.handler
    events:
      - apigw:
          path: /{proxy+}
          method: ANY
    environment:
      QWEN_API_KEY: ${env:QWEN_API_KEY}
      FEISHU_APP_ID: ${env:FEISHU_APP_ID}
      FEISHU_APP_SECRET: ${env:FEISHU_APP_SECRET}

plugins:
  - serverless-python-requirements
```

#### 部署脚本
```bash
#!/bin/bash
# scripts/deploy-scf.sh

echo "开始部署到腾讯云函数..."

# 1. 安装依赖
cd backend
pip install -r requirements.txt -t ./package

# 2. 打包代码
zip -r function.zip app/ package/

# 3. 部署（使用腾讯云 CLI）
tccli scf UpdateFunctionCode \
  --FunctionName feishu-formatter \
  --Handler app.main.handler \
  --ZipFile fileb://function.zip

echo "部署完成！"
echo "API 地址: https://service-xxx.gz.apigw.tencentcs.com/release/"
```

### 4. 性能优化

#### 前端优化
1. **代码分割**：按需加载组件
2. **缓存策略**：缓存 API 响应（5 分钟）
3. **防抖处理**：避免频繁调用分析接口

#### 后端优化
1. **批量处理**：一次分析多个 Block
2. **超时控制**：AI 调用超时 10 秒
3. **降级策略**：AI 失败时使用规则引擎
4. **并发限制**：限制单用户并发请求

#### AI 调用优化
```python
class AIAnalyzer:
    def __init__(self):
        self.cache = {}  # 简单内存缓存

    async def analyze_document(self, blocks: List[Dict], config: Dict) -> List[Dict]:
        # 1. 计算文档指纹（用于缓存）
        content_hash = hashlib.md5(
            json.dumps(blocks, sort_keys=True).encode()
        ).hexdigest()

        # 2. 检查缓存
        if content_hash in self.cache:
            return self.cache[content_hash]

        # 3. 调用 AI
        suggestions = await self._call_ai(blocks, config)

        # 4. 缓存结果（5 分钟）
        self.cache[content_hash] = suggestions

        return suggestions
```

---

## 总结

### 方案选择理由

| 决策点 | 理由 |
|--------|------|
| **Serverless 架构** | 平衡安全性、成本、运维复杂度的最优解 |
| **Client API + 后端代理** | 前端操作文档，后端仅负责 AI 调用 |
| **通义千问** | 中文能力强，性价比高，响应快 |
| **React + TypeScript** | 生态成熟，类型安全，飞书官方支持 |
| **FastAPI** | 高性能异步，Serverless 友好 |

### 关键技术决策

1. **放弃纯前端方案**：API Key 安全问题无解
2. **选择 Serverless**：比传统服务器更适合这个场景
3. **前端 CDN 托管**：利用飞书基础设施，零成本
4. **轻量级后端**：仅作为 AI 调用代理，最小化功能

### 成本估算

**开发阶段**：
- 人力：5-7 天（1 人）
- 费用：¥0（使用免费额度）

**运营阶段**（按月 1000 次调用计算）：
- 云函数调用：¥0.1
- 通义千问 API：¥3-5
- 飞书 API：免费
- **总计：¥5/月以内**

**对比传统服务器**：
- 最低配 1 核 2G：¥60-100/月
- 节省 90%+ 成本

---

## 附录

### 参考资料
1. [飞书开放平台文档](https://open.feishu.cn/document/)
2. [飞书文档 Block API](https://open.feishu.cn/document/ukTMukTMukTM/uYDN04iN0QjL2QDN)
3. [通义千问 API 文档](https://help.aliyun.com/zh/dashscope/)
4. [FastAPI 官方文档](https://fastapi.tiangolo.com/)
5. [腾讯云函数文档](https://cloud.tencent.com/document/product/583)

### 项目代码结构
```
feishu/doc-reformat/
├── frontend/              # 前端（飞书 CDN 托管）
│   ├── src/
│   │   ├── components/   # React 组件
│   │   ├── api/          # API 封装
│   │   ├── types/        # TypeScript 类型
│   │   └── utils/        # 工具函数
│   └── package.json
├── backend/              # 后端（Serverless 云函数）
│   ├── app/
│   │   ├── main.py      # FastAPI 主程序
│   │   ├── ai.py        # AI 分析模块
│   │   └── feishu.py    # 飞书 API 封装
│   └── requirements.txt
├── scripts/              # 部署脚本
│   ├── deploy-scf.sh    # 腾讯云部署
│   └── deploy-fc.sh     # 阿里云部署
└── docs/                 # 项目文档
    ├── TECHNICAL_ANALYSIS.md   # 本文档
    ├── QUICKSTART.md
    ├── DEVELOPMENT.md
    ├── DEPLOYMENT.md
    └── FEISHU_SETUP.md
```

---

**文档版本**：v1.0
**最后更新**：2026-01-20
**作者**：Claude Code AI Assistant
