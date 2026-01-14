import React, { useEffect, useState } from 'react';
import { ConfigProvider, theme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { FormatterPanel } from './components/FormatterPanel';

function App() {
  const [documentId, setDocumentId] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 从URL参数或飞书环境获取文档ID
    const params = new URLSearchParams(window.location.search);
    const docId = params.get('document_id') || 'test_doc_id';
    setDocumentId(docId);
    setLoading(false);

    // TODO: 集成飞书SDK获取文档上下文
    // 参考: https://open.feishu.cn/document/client-docs/docs-add-on/
  }, []);

  if (loading) {
    return <div>加载中...</div>;
  }

  if (!documentId) {
    return <div>无法获取文档ID</div>;
  }

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <div style={{ padding: '24px', minHeight: '100vh', background: '#f5f5f5' }}>
        <FormatterPanel documentId={documentId} />
      </div>
    </ConfigProvider>
  );
}

export default App;
