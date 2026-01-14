"""
FastAPI主应用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import uvicorn

from .config import settings
from .feishu import feishu_client
from .ai import ai_analyzer

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="飞书文档一键排版API",
    description="基于AI的飞书文档智能排版服务",
    version="1.0.0",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求/响应模型
class AnalyzeRequest(BaseModel):
    """分析请求"""
    document_id: str
    config: Optional[Dict[str, Any]] = {
        "optimization_level": "standard",
        "enable_list_conversion": True,
        "enable_table_conversion": True,
        "enable_callout_conversion": True,
        "enable_heading_optimization": True,
    }


class ApplyRequest(BaseModel):
    """应用优化请求"""
    document_id: str
    suggestion_ids: List[str]


class ApiResponse(BaseModel):
    """API响应"""
    code: int
    message: str
    data: Optional[Any] = None


# API路由
@app.get("/")
async def root():
    """根路径"""
    return {"message": "飞书文档一键排版API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return ApiResponse(
        code=0,
        message="服务正常",
        data={"status": "healthy"}
    )


@app.post("/api/analyze")
async def analyze_document(request: AnalyzeRequest):
    """
    分析文档

    Args:
        request: 分析请求

    Returns:
        分析结果
    """
    try:
        logger.info(f"开始分析文档: {request.document_id}")

        # 1. 获取文档所有Block
        blocks = await feishu_client.get_document_blocks(request.document_id)

        if not blocks:
            return ApiResponse(
                code=1001,
                message="无法获取文档内容或文档为空",
            )

        # 2. AI分析
        analysis_result = await ai_analyzer.analyze_document(blocks, request.config)

        logger.info(f"分析完成: 发现 {analysis_result['optimizable_blocks']} 处可优化")

        return ApiResponse(
            code=0,
            message="分析成功",
            data={
                "document_id": request.document_id,
                **analysis_result,
            }
        )

    except Exception as e:
        logger.error(f"分析文档异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/apply")
async def apply_optimization(request: ApplyRequest):
    """
    应用优化

    Args:
        request: 应用请求

    Returns:
        应用结果
    """
    try:
        logger.info(f"开始应用优化: 文档={request.document_id}, 数量={len(request.suggestion_ids)}")

        # TODO: 实现具体的Block更新逻辑
        # 1. 根据suggestion_ids获取具体的优化操作
        # 2. 调用飞书API批量更新Block
        # 3. 返回结果

        # 临时返回成功
        return ApiResponse(
            code=0,
            message="优化应用成功",
            data={
                "updated_count": len(request.suggestion_ids),
            }
        )

    except Exception as e:
        logger.error(f"应用优化异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/document/{document_id}")
async def get_document_info(document_id: str):
    """
    获取文档信息

    Args:
        document_id: 文档ID

    Returns:
        文档信息
    """
    try:
        blocks = await feishu_client.get_document_blocks(document_id)

        return ApiResponse(
            code=0,
            message="获取成功",
            data={
                "document_id": document_id,
                "block_count": len(blocks),
            }
        )

    except Exception as e:
        logger.error(f"获取文档信息异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # 启动服务
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
