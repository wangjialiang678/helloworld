import axios from 'axios';
import { AnalysisResult, ApiResponse, FormatterConfig } from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// API方法
export const documentAPI = {
  // 分析文档
  analyze: async (
    documentId: string,
    config: Partial<FormatterConfig> = {}
  ): Promise<ApiResponse<AnalysisResult>> => {
    return api.post('/analyze', {
      document_id: documentId,
      config,
    });
  },

  // 应用优化
  applyOptimization: async (
    documentId: string,
    suggestionIds: string[]
  ): Promise<ApiResponse> => {
    return api.post('/apply', {
      document_id: documentId,
      suggestion_ids: suggestionIds,
    });
  },

  // 获取文档信息
  getDocumentInfo: async (documentId: string): Promise<ApiResponse> => {
    return api.get(`/document/${documentId}`);
  },

  // 健康检查
  healthCheck: async (): Promise<ApiResponse> => {
    return api.get('/health');
  },
};

export default api;
