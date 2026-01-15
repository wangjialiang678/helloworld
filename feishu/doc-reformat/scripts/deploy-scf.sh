#!/bin/bash
# 腾讯云函数(SCF)部署脚本

set -e

echo "开始部署到腾讯云函数..."

# 检查是否安装了腾讯云CLI
if ! command -v scf &> /dev/null; then
    echo "错误: 未安装腾讯云CLI工具"
    echo "请先安装: pip install scf-cli"
    exit 1
fi

# 进入后端目录
cd "$(dirname "$0")/../backend"

# 创建部署包
echo "创建部署包..."
rm -rf deploy_package
mkdir -p deploy_package

# 复制代码
cp -r app deploy_package/

# 安装依赖到部署包
pip install -r requirements.txt -t deploy_package/ -i https://pypi.tuna.tsinghua.edu.cn/simple

# 打包
cd deploy_package
zip -r ../feishu-doc-formatter.zip .
cd ..

echo "部署包创建完成: feishu-doc-formatter.zip"

# 部署到云函数
echo "部署到腾讯云函数..."

# 配置环境变量
export FEISHU_APP_ID="${FEISHU_APP_ID}"
export FEISHU_APP_SECRET="${FEISHU_APP_SECRET}"
export QWEN_API_KEY="${QWEN_API_KEY}"

# 使用腾讯云CLI部署
# 注意: 需要先在腾讯云控制台创建函数，然后使用CLI更新代码
scf deploy \
    --name feishu-doc-formatter \
    --runtime Python39 \
    --handler app.main.app \
    --code-file feishu-doc-formatter.zip \
    --memory 512 \
    --timeout 30 \
    --env "FEISHU_APP_ID=${FEISHU_APP_ID},FEISHU_APP_SECRET=${FEISHU_APP_SECRET},QWEN_API_KEY=${QWEN_API_KEY}"

echo "部署完成!"
echo "请在腾讯云控制台配置API网关触发器"
