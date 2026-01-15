#!/bin/bash
# 阿里云函数计算(FC)部署脚本

set -e

echo "开始部署到阿里云函数计算..."

# 检查是否安装了阿里云CLI
if ! command -v fun &> /dev/null; then
    echo "错误: 未安装阿里云Fun工具"
    echo "请先安装: npm install -g @alicloud/fun"
    exit 1
fi

# 进入项目根目录
cd "$(dirname "$0")/.."

# 创建template.yml (阿里云函数计算配置)
cat > template.yml <<EOF
ROSTemplateFormatVersion: '2015-09-01'
Transform: 'Aliyun::Serverless-2018-04-03'
Resources:
  feishu-doc-formatter:
    Type: 'Aliyun::Serverless::Service'
    Properties:
      Description: '飞书文档一键排版服务'
    feishu-formatter-api:
      Type: 'Aliyun::Serverless::Function'
      Properties:
        Handler: app.main.app
        Runtime: python3.9
        CodeUri: ./backend
        MemorySize: 512
        Timeout: 30
        EnvironmentVariables:
          FEISHU_APP_ID: \${FEISHU_APP_ID}
          FEISHU_APP_SECRET: \${FEISHU_APP_SECRET}
          QWEN_API_KEY: \${QWEN_API_KEY}
      Events:
        httpTrigger:
          Type: HTTP
          Properties:
            AuthType: ANONYMOUS
            Methods: ['GET', 'POST', 'PUT', 'DELETE']
EOF

echo "配置文件创建完成"

# 安装依赖
echo "安装依赖..."
cd backend
pip install -r requirements.txt -t . -i https://pypi.tuna.tsinghua.edu.cn/simple
cd ..

# 部署
echo "部署到阿里云..."
fun deploy

echo "部署完成!"
echo "函数地址将在控制台显示"
