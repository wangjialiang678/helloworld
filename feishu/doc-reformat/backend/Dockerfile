FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY app ./app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "app.main"]
