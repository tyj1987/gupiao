# 股票AI分析系统 - 多阶段构建 Dockerfile
# 构建者: tyj1987 <tuoyongjun1987@qq.com>
# 版本: 2.1.0

# ==============================================================================
# 阶段1: 构建阶段
# ==============================================================================
FROM python:3.10-slim as builder

# 构建参数
ARG BUILDTIME
ARG VERSION
ARG REVISION

# 设置构建环境
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制并安装依赖
COPY requirements*.txt ./
RUN pip install --user --no-warn-script-location \
    -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/

# ==============================================================================
# 阶段2: 运行时阶段
# ==============================================================================
FROM python:3.10-slim as runtime

# 元数据标签
LABEL maintainer="tyj1987 <tuoyongjun1987@qq.com>"
LABEL org.opencontainers.image.title="股票AI分析系统"
LABEL org.opencontainers.image.description="基于AI的股票分析和预测系统"
LABEL org.opencontainers.image.vendor="tyj1987"
LABEL org.opencontainers.image.version="${VERSION:-latest}"
LABEL org.opencontainers.image.created="${BUILDTIME}"
LABEL org.opencontainers.image.revision="${REVISION}"
LABEL org.opencontainers.image.source="https://github.com/tyj1987/gupiao"
LABEL org.opencontainers.image.documentation="https://github.com/tyj1987/gupiao/blob/main/README.md"

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置工作目录
WORKDIR /app

# 从构建阶段复制Python包
COPY --from=builder /root/.local /home/appuser/.local

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV PATH=/home/appuser/.local/bin:$PATH

# 复制应用代码
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser config/ ./config/
COPY --chown=appuser:appuser main.py ./
COPY --chown=appuser:appuser simple_app.py ./

# 创建必要的目录
RUN mkdir -p /app/data /app/cache /app/logs /app/models && \
    chown -R appuser:appuser /app

# 创建健康检查脚本
RUN echo '#!/bin/bash\ncurl -f http://localhost:8501/_stcore/health || exit 1' > /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh && \
    chown appuser:appuser /app/healthcheck.sh

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

# 启动命令
CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]
CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
