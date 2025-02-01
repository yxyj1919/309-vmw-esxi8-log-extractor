# 使用 Python 3.10 作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY app/ ./app/
COPY data/ ./data/

# 创建必要的目录
RUN mkdir -p logs reports output

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Streamlit 默认端口
EXPOSE 8501

# 设置健康检查
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 启动命令
CMD ["streamlit", "run", "app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]

# 添加元数据标签
LABEL maintainer="Your Name <your.email@example.com>" \
      version="1.0" \
      description="VMware ESXi Log Analyzer" 