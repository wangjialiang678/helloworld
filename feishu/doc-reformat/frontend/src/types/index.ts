// 飞书Block类型
export enum BlockType {
  Page = 1,
  Text = 2,
  Heading1 = 3,
  Heading2 = 4,
  Heading3 = 5,
  Heading4 = 6,
  Heading5 = 7,
  Heading6 = 8,
  Heading7 = 9,
  Heading8 = 10,
  Heading9 = 11,
  Bullet = 12,
  Ordered = 13,
  Code = 14,
  Quote = 15,
  Equation = 16,
  Todo = 17,
  Bitable = 18,
  Callout = 19,
  ChatCard = 20,
  Diagram = 21,
  Divider = 22,
  File = 23,
  Grid = 24,
  GridColumn = 25,
  Iframe = 26,
  Image = 27,
  ISV = 28,
  Mindnote = 29,
  Sheet = 30,
  Table = 31,
  TableCell = 32,
  View = 33,
  UndefinedBlock = 34,
  QuoteContainer = 35,
  Task = 36,
  OKR = 37,
  OKRObjective = 38,
  OKRKeyResult = 39,
  OKRProgress = 40,
  AddOns = 41,
  Jira = 42,
  Wiki = 43,
  Board = 44,
  UNDEFINED = 999,
}

// Block数据结构
export interface Block {
  block_id: string;
  block_type: BlockType;
  parent_id?: string;
  children?: string[];
  text?: {
    elements: TextElement[];
  };
  [key: string]: any;
}

// 文本元素
export interface TextElement {
  text_run?: {
    content: string;
    text_element_style?: {
      bold?: boolean;
      italic?: boolean;
      strikethrough?: boolean;
      underline?: boolean;
    };
  };
}

// 优化建议
export interface OptimizationSuggestion {
  block_id: string;
  original_type: BlockType;
  suggested_type: BlockType;
  reason: string;
  confidence: number;
  preview?: {
    before: string;
    after: string;
  };
  metadata?: {
    list_items?: string[];
    table_data?: {
      headers: string[];
      rows: string[][];
    };
    callout_config?: {
      emoji: string;
      background_color: string;
      border_color?: string;
    };
  };
}

// 分析结果
export interface AnalysisResult {
  document_id: string;
  total_blocks: number;
  optimizable_blocks: number;
  suggestions: OptimizationSuggestion[];
  estimated_improvement: number; // 0-100
}

// API响应
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
}

// 格式化配置
export interface FormatterConfig {
  optimization_level: 'conservative' | 'standard' | 'aggressive';
  enable_list_conversion: boolean;
  enable_table_conversion: boolean;
  enable_callout_conversion: boolean;
  enable_heading_optimization: boolean;
  preserve_user_formatting: boolean;
}
