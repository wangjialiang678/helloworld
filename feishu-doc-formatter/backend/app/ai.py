"""
AI分析模块 - 使用通义千问
"""
import dashscope
from dashscope import Generation
from typing import List, Dict, Any
import json
import logging
from .config import settings

logger = logging.getLogger(__name__)

# 设置API Key
dashscope.api_key = settings.qwen_api_key


class AIAnalyzer:
    """AI文档分析器"""

    def __init__(self):
        self.model = "qwen-plus"  # 使用通义千问Plus模型

    async def analyze_document(
        self,
        blocks: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析文档并生成优化建议

        Args:
            blocks: 文档Block列表
            config: 配置选项

        Returns:
            分析结果
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(blocks, config)

            # 调用AI模型
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                result_format='message',
                temperature=0.3,  # 较低的temperature使结果更稳定
            )

            if response.status_code == 200:
                # 解析AI响应
                ai_response = response.output.choices[0].message.content
                suggestions = self._parse_ai_response(ai_response, blocks)

                return {
                    "total_blocks": len(blocks),
                    "optimizable_blocks": len(suggestions),
                    "suggestions": suggestions,
                    "estimated_improvement": self._calculate_improvement(suggestions),
                }
            else:
                logger.error(f"AI调用失败: {response.message}")
                return self._get_fallback_analysis(blocks)

        except Exception as e:
            logger.error(f"AI分析异常: {e}")
            return self._get_fallback_analysis(blocks)

    def _build_prompt(
        self,
        blocks: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> str:
        """构建AI提示词"""

        # 简化Block信息用于分析
        simplified_blocks = []
        for i, block in enumerate(blocks):
            simplified_blocks.append({
                "index": i,
                "block_id": block.get("block_id"),
                "type": block.get("block_type"),
                "content": self._extract_block_content(block)[:200],  # 限制长度
            })

        prompt = f"""你是一个专业的文档排版助手。请分析以下飞书文档内容，识别哪些部分需要优化格式。

优化级别: {config.get('optimization_level', 'standard')}

可用的优化类型:
1. 转换为列表 (bullet=12, ordered=13): 适用于并列的多个要点
2. 转换为高亮块 (callout=19): 适用于重要提示、警告、注意事项
3. 转换为表格 (table=31): 适用于结构化数据、对比信息
4. 优化标题层级 (heading1-9): 调整标题结构

文档Block内容:
{json.dumps(simplified_blocks[:50], ensure_ascii=False, indent=2)}

请以JSON格式返回优化建议，格式如下:
{{
  "suggestions": [
    {{
      "block_index": 0,
      "original_type": 2,
      "suggested_type": 12,
      "reason": "这段内容包含多个并列要点，适合转换为无序列表",
      "confidence": 0.85,
      "metadata": {{
        "list_items": ["要点1", "要点2", "要点3"]
      }}
    }}
  ]
}}

注意:
- 只返回需要优化的Block
- confidence范围: 0.0-1.0
- 确保建议合理且可操作
"""
        return prompt

    def _extract_block_content(self, block: Dict[str, Any]) -> str:
        """提取Block的文本内容"""
        # 简化版本,实际需要根据Block类型提取
        # TODO: 完善Block内容提取逻辑
        return str(block.get("content", ""))[:200]

    def _parse_ai_response(
        self,
        ai_response: str,
        original_blocks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """解析AI响应"""
        try:
            # 尝试从响应中提取JSON
            # AI可能返回带有解释的文本,需要提取JSON部分
            json_start = ai_response.find("{")
            json_end = ai_response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = ai_response[json_start:json_end]
                result = json.loads(json_str)

                suggestions = result.get("suggestions", [])

                # 补充完整的Block信息
                for suggestion in suggestions:
                    block_index = suggestion.get("block_index")
                    if 0 <= block_index < len(original_blocks):
                        suggestion["block_id"] = original_blocks[block_index].get("block_id")

                        # 生成预览
                        suggestion["preview"] = {
                            "before": self._generate_preview(
                                original_blocks[block_index],
                                suggestion["original_type"]
                            ),
                            "after": self._generate_preview(
                                original_blocks[block_index],
                                suggestion["suggested_type"],
                                suggestion.get("metadata", {})
                            ),
                        }

                return suggestions

        except json.JSONDecodeError as e:
            logger.error(f"解析AI响应JSON失败: {e}")

        return []

    def _generate_preview(
        self,
        block: Dict[str, Any],
        block_type: int,
        metadata: Dict[str, Any] = None
    ) -> str:
        """生成预览文本"""
        content = self._extract_block_content(block)

        if block_type == 12:  # 无序列表
            if metadata and "list_items" in metadata:
                return "• " + "\n• ".join(metadata["list_items"])
            return f"• {content}"

        elif block_type == 13:  # 有序列表
            if metadata and "list_items" in metadata:
                return "\n".join(
                    f"{i+1}. {item}" for i, item in enumerate(metadata["list_items"])
                )
            return f"1. {content}"

        elif block_type == 19:  # 高亮块
            emoji = metadata.get("callout_config", {}).get("emoji", "💡") if metadata else "💡"
            return f"{emoji} {content}"

        elif block_type == 31:  # 表格
            return "[表格预览]"

        return content

    def _calculate_improvement(self, suggestions: List[Dict[str, Any]]) -> int:
        """计算预估改进效果 (0-100)"""
        if not suggestions:
            return 0

        # 根据建议数量和置信度计算
        total_confidence = sum(s.get("confidence", 0.5) for s in suggestions)
        avg_confidence = total_confidence / len(suggestions)

        # 简化计算: 建议数量 * 平均置信度 * 权重
        improvement = min(100, int(len(suggestions) * avg_confidence * 10))
        return improvement

    def _get_fallback_analysis(
        self,
        blocks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """AI失败时的降级分析"""
        # 使用简单规则进行基础分析
        suggestions = []

        for i, block in enumerate(blocks):
            content = self._extract_block_content(block)

            # 简单规则: 包含多个"、"或"，"的段落转为列表
            if block.get("block_type") == 2 and ("、" in content or "，" in content):
                suggestions.append({
                    "block_id": block.get("block_id"),
                    "block_index": i,
                    "original_type": 2,
                    "suggested_type": 12,
                    "reason": "检测到多个并列项，建议转换为列表",
                    "confidence": 0.6,
                    "preview": {
                        "before": content,
                        "after": f"• {content}",
                    },
                })

        return {
            "total_blocks": len(blocks),
            "optimizable_blocks": len(suggestions),
            "suggestions": suggestions,
            "estimated_improvement": 30,
        }


# 全局分析器实例
ai_analyzer = AIAnalyzer()
