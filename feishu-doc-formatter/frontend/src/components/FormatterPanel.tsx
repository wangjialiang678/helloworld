import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Progress,
  List,
  Tag,
  Space,
  Typography,
  Divider,
  Alert,
  Spin,
  Checkbox,
  Radio,
} from 'antd';
import {
  CheckCircleOutlined,
  SyncOutlined,
  ThunderboltOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { documentAPI } from '../api';
import {
  AnalysisResult,
  OptimizationSuggestion,
  FormatterConfig,
  BlockType,
} from '../types';

const { Title, Text, Paragraph } = Typography;

interface FormatterPanelProps {
  documentId: string;
}

// Block类型映射为中文
const blockTypeNames: Record<number, string> = {
  [BlockType.Text]: '段落',
  [BlockType.Bullet]: '无序列表',
  [BlockType.Ordered]: '有序列表',
  [BlockType.Callout]: '高亮块',
  [BlockType.Table]: '表格',
  [BlockType.Heading1]: '一级标题',
  [BlockType.Heading2]: '二级标题',
  [BlockType.Heading3]: '三级标题',
};

export const FormatterPanel: React.FC<FormatterPanelProps> = ({
  documentId,
}) => {
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [applying, setApplying] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [selectedSuggestions, setSelectedSuggestions] = useState<string[]>([]);
  const [config, setConfig] = useState<FormatterConfig>({
    optimization_level: 'standard',
    enable_list_conversion: true,
    enable_table_conversion: true,
    enable_callout_conversion: true,
    enable_heading_optimization: true,
    preserve_user_formatting: true,
  });

  // 自动分析文档
  useEffect(() => {
    handleAnalyze();
  }, [documentId]);

  // 分析文档
  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      const response = await documentAPI.analyze(documentId, config);
      if (response.code === 0 && response.data) {
        setAnalysisResult(response.data);
        // 默认选中所有建议
        setSelectedSuggestions(
          response.data.suggestions.map((s) => s.block_id)
        );
      }
    } catch (error) {
      console.error('分析失败:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  // 应用优化
  const handleApply = async () => {
    if (!selectedSuggestions.length) return;

    setApplying(true);
    try {
      const response = await documentAPI.applyOptimization(
        documentId,
        selectedSuggestions
      );
      if (response.code === 0) {
        // 成功提示
        alert('文档优化完成！');
      }
    } catch (error) {
      console.error('应用失败:', error);
    } finally {
      setApplying(false);
    }
  };

  // 切换建议选择
  const toggleSuggestion = (blockId: string) => {
    setSelectedSuggestions((prev) =>
      prev.includes(blockId)
        ? prev.filter((id) => id !== blockId)
        : [...prev, blockId]
    );
  };

  // 渲染优化建议
  const renderSuggestion = (suggestion: OptimizationSuggestion) => {
    const isSelected = selectedSuggestions.includes(suggestion.block_id);
    const confidence = Math.round(suggestion.confidence * 100);

    return (
      <List.Item
        key={suggestion.block_id}
        style={{
          background: isSelected ? '#f0f9ff' : '#fff',
          padding: '12px',
          borderRadius: '8px',
          marginBottom: '8px',
          border: isSelected ? '1px solid #1890ff' : '1px solid #f0f0f0',
          cursor: 'pointer',
        }}
        onClick={() => toggleSuggestion(suggestion.block_id)}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Checkbox checked={isSelected} />
            <Tag color="blue">
              {blockTypeNames[suggestion.original_type] || '未知'}
            </Tag>
            <Text>→</Text>
            <Tag color="green">
              {blockTypeNames[suggestion.suggested_type] || '未知'}
            </Tag>
            <Tag color={confidence > 80 ? 'success' : 'warning'}>
              置信度: {confidence}%
            </Tag>
          </Space>

          <Text type="secondary">{suggestion.reason}</Text>

          {suggestion.preview && (
            <>
              <Divider style={{ margin: '8px 0' }} />
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong>优化前:</Text>
                <Paragraph
                  style={{
                    background: '#fafafa',
                    padding: '8px',
                    borderRadius: '4px',
                    margin: 0,
                  }}
                >
                  {suggestion.preview.before}
                </Paragraph>
                <Text strong>优化后:</Text>
                <Paragraph
                  style={{
                    background: '#f6ffed',
                    padding: '8px',
                    borderRadius: '4px',
                    margin: 0,
                  }}
                >
                  {suggestion.preview.after}
                </Paragraph>
              </Space>
            </>
          )}
        </Space>
      </List.Item>
    );
  };

  if (analyzing) {
    return (
      <Card>
        <Space
          direction="vertical"
          align="center"
          style={{ width: '100%', padding: '40px 0' }}
        >
          <Spin size="large" />
          <Title level={4}>AI正在分析文档...</Title>
          <Text type="secondary">
            正在使用AI模型分析文档结构，预计需要5-10秒
          </Text>
        </Space>
      </Card>
    );
  }

  if (!analysisResult) {
    return (
      <Card>
        <Alert message="无法加载分析结果" type="error" />
      </Card>
    );
  }

  return (
    <Card style={{ maxWidth: 800, margin: '0 auto' }}>
      {/* 标题 */}
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <div>
          <Title level={3}>
            <ThunderboltOutlined /> AI文档一键排版
          </Title>
          <Text type="secondary">
            AI已分析文档，发现 {analysisResult.optimizable_blocks} 处可优化内容
          </Text>
        </div>

        {/* 预估提升 */}
        <Card size="small" style={{ background: '#f6ffed' }}>
          <Space>
            <Text strong>预计优化效果:</Text>
            <Progress
              percent={analysisResult.estimated_improvement}
              steps={10}
              strokeColor="#52c41a"
            />
          </Space>
        </Card>

        {/* 配置选项 */}
        <Card size="small" title="优化级别">
          <Radio.Group
            value={config.optimization_level}
            onChange={(e) =>
              setConfig({ ...config, optimization_level: e.target.value })
            }
          >
            <Radio.Button value="conservative">保守</Radio.Button>
            <Radio.Button value="standard">标准</Radio.Button>
            <Radio.Button value="aggressive">激进</Radio.Button>
          </Radio.Group>
        </Card>

        {/* 优化建议列表 */}
        <div>
          <Space style={{ marginBottom: 16 }}>
            <Text strong>优化建议 ({analysisResult.suggestions.length})</Text>
            <Button
              size="small"
              onClick={() =>
                setSelectedSuggestions(
                  selectedSuggestions.length === analysisResult.suggestions.length
                    ? []
                    : analysisResult.suggestions.map((s) => s.block_id)
                )
              }
            >
              {selectedSuggestions.length === analysisResult.suggestions.length
                ? '取消全选'
                : '全选'}
            </Button>
          </Space>

          <List
            dataSource={analysisResult.suggestions}
            renderItem={renderSuggestion}
            style={{ maxHeight: '400px', overflowY: 'auto' }}
          />
        </div>

        {/* 操作按钮 */}
        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
          <Button onClick={handleAnalyze} icon={<SyncOutlined />}>
            重新分析
          </Button>
          <Button
            type="primary"
            size="large"
            icon={<CheckCircleOutlined />}
            loading={applying}
            disabled={!selectedSuggestions.length}
            onClick={handleApply}
          >
            应用优化 ({selectedSuggestions.length})
          </Button>
        </Space>
      </Space>
    </Card>
  );
};
