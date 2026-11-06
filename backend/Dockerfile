# =============================================================================
# AlphaHunter 后端镜像
# 构建：docker build -t alphahunter-backend ./backend
# 说明：使用 Python 3.12 slim 镜像，SQLite 数据通过 volume 持久化。
# =============================================================================
FROM python:3.12-slim

# Python 运行优化：
# - 不生成 .pyc 文件
# - 标准输出不缓冲，便于容器日志实时采集
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# LightGBM / XGBoost 的 Linux 轮子依赖 OpenMP 运行库（libgomp）。
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 先复制依赖清单，充分利用 Docker 层缓存
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# 再复制应用代码
COPY app ./app

# 数据目录用于 SQLite；容器中建议挂载 volume
RUN mkdir -p /app/data

EXPOSE 8000

# 健康检查直接使用 Python 标准库，避免额外安装 curl
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=3)" || exit 1

# 生产启动参数：单进程便于 SQLite 使用；切换 PostgreSQL 后可增加 workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
