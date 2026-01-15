"""
飞书API封装模块
"""
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *
from typing import List, Dict, Any, Optional
from .config import settings
import logging

logger = logging.getLogger(__name__)


class FeishuClient:
    """飞书API客户端"""

    def __init__(self):
        self.client = lark.Client.builder() \
            .app_id(settings.feishu_app_id) \
            .app_secret(settings.feishu_app_secret) \
            .log_level(lark.LogLevel.DEBUG if settings.debug else lark.LogLevel.INFO) \
            .build()

    async def get_document_blocks(self, document_id: str) -> List[Dict[str, Any]]:
        """
        获取文档所有Block

        Args:
            document_id: 文档ID

        Returns:
            Block列表
        """
        try:
            blocks = []
            page_token = None

            while True:
                # 构建请求
                request = ListDocumentBlockRequest.builder() \
                    .document_id(document_id) \
                    .page_size(500) \
                    .page_token(page_token) \
                    .build()

                # 调用API
                response = self.client.docx.v1.document_block.list(request)

                if not response.success():
                    logger.error(
                        f"获取文档Block失败: {response.code} - {response.msg}"
                    )
                    break

                if response.data and response.data.items:
                    blocks.extend([self._block_to_dict(block) for block in response.data.items])

                # 检查是否还有更多数据
                if not response.data.has_more:
                    break

                page_token = response.data.page_token

            logger.info(f"获取文档 {document_id} 共 {len(blocks)} 个Block")
            return blocks

        except Exception as e:
            logger.error(f"获取文档Block异常: {e}")
            return []

    async def batch_update_blocks(
        self,
        document_id: str,
        block_updates: List[Dict[str, Any]]
    ) -> bool:
        """
        批量更新Block

        Args:
            document_id: 文档ID
            block_updates: Block更新列表

        Returns:
            是否成功
        """
        try:
            # 飞书建议每次不超过10个Block
            batch_size = 10
            for i in range(0, len(block_updates), batch_size):
                batch = block_updates[i:i + batch_size]
                await self._update_batch(document_id, batch)

            logger.info(f"批量更新 {len(block_updates)} 个Block成功")
            return True

        except Exception as e:
            logger.error(f"批量更新Block异常: {e}")
            return False

    async def _update_batch(
        self,
        document_id: str,
        batch: List[Dict[str, Any]]
    ):
        """更新一批Block"""
        for block_update in batch:
            block_id = block_update.get("block_id")
            block_type = block_update.get("block_type")
            content = block_update.get("content")

            # 根据不同的Block类型调用不同的更新API
            # 这里简化处理,实际需要根据具体的Block类型构建请求
            logger.debug(f"更新Block {block_id} 为类型 {block_type}")

            # TODO: 实现具体的Block更新逻辑
            # 参考: https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block-children/create

    async def create_block(
        self,
        document_id: str,
        parent_block_id: str,
        block_type: int,
        content: Dict[str, Any]
    ) -> Optional[str]:
        """
        创建新Block

        Args:
            document_id: 文档ID
            parent_block_id: 父Block ID
            block_type: Block类型
            content: Block内容

        Returns:
            新Block的ID
        """
        try:
            # 构建Block数据
            # 这里需要根据具体的Block类型构建请求
            logger.info(f"创建新Block: type={block_type}")

            # TODO: 实现具体的Block创建逻辑
            return None

        except Exception as e:
            logger.error(f"创建Block异常: {e}")
            return None

    async def delete_block(
        self,
        document_id: str,
        block_id: str
    ) -> bool:
        """
        删除Block

        Args:
            document_id: 文档ID
            block_id: Block ID

        Returns:
            是否成功
        """
        try:
            # 构建请求
            request = DeleteDocumentBlockChildrenRequest.builder() \
                .document_id(document_id) \
                .block_id(block_id) \
                .build()

            # 调用API
            response = self.client.docx.v1.document_block_children.delete(request)

            if not response.success():
                logger.error(f"删除Block失败: {response.code} - {response.msg}")
                return False

            logger.info(f"删除Block {block_id} 成功")
            return True

        except Exception as e:
            logger.error(f"删除Block异常: {e}")
            return False

    def _block_to_dict(self, block: DocumentBlock) -> Dict[str, Any]:
        """将Block对象转换为字典"""
        return {
            "block_id": block.block_id,
            "block_type": block.block_type,
            "parent_id": block.parent_id,
            "children": block.children if hasattr(block, 'children') else [],
            # 更多字段根据需要添加
        }


# 全局客户端实例
feishu_client = FeishuClient()
