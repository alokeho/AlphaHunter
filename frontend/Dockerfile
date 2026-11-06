# =============================================================================
# AlphaHunter 前端镜像
# 构建：docker build -t alphahunter-frontend ./frontend
# 说明：多阶段构建，最终镜像仅包含 Nginx 与静态文件。
# =============================================================================
FROM node:22-alpine AS builder

WORKDIR /app

# 使用与本地锁文件一致的 pnpm 主版本
RUN npm install -g pnpm@11.28.5

# 先复制依赖描述，最大化利用 Docker 缓存
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

# 复制源码并构建
COPY . .
RUN pnpm build

FROM nginx:1.27-alpine

# 自定义 Nginx 配置：SPA history fallback + /api 反向代理
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
