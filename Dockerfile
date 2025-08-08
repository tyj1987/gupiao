# =============================================
# 股票AI分析系统 - 精简版 Dockerfile
# 构建者: tyj1987 <tuoyongjun1987@qq.com>
# 版本: 2.1.1 (优化版)
# =============================================

# 使用 Python 3.9 slim 镜像作为基础
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 一次性安装系统依赖并清理
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制并安装 Python 依赖
COPY requirements_minimal_fixed.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements_minimal_fixed.txt && \
    pip cache purge

# 复制应用核心文件
COPY src/ ./src/
COPY config/ ./config/
COPY .streamlit/ ./.streamlit/

# 创建必要的目录
RUN mkdir -p logs cache data exports

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 启动应用
CMD ["python", "-m", "streamlit", "run", "src/ui/streamlit_app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true", \
     "--browser.gatherUsageStats", "false"]
