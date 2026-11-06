# AlphaHunter

**A 股 AI 量化选股平台 · 第一阶段：基础框架**

AlphaHunter 是一个面向 A 股量化研究的全栈平台。项目目标是建立从「数据接入 → 因子研究 → AI 选股 → 策略回测 → 组合跟踪」的可复现研究流水线。

当前仓库完成 **Phase 1（基础框架）**，重点是可运行的工程底座，而不是完整的选股策略。

> **研究声明**：本项目仅用于量化研究、教学与工程实践，不构成任何投资建议。当前阶段展示的股票为公开静态演示数据，不包含实时行情、收益曲线或交易信号。

---

## 1. 第一阶段交付范围

### 已完成

- [x] 模块化全栈目录结构，后端 / 前端 / 测试 / Docker 分层清晰
- [x] Python 3.12 + FastAPI 服务，自动生成 OpenAPI / Swagger 文档
- [x] SQLAlchemy 2.0 ORM + SQLite 数据库，应用启动时自动建表
- [x] 股票（stocks）与日行情（daily_bars）两张核心表
- [x] 幂等的数据库初始化脚本与演示股票种子数据
- [x] 统一业务异常、参数校验异常与未处理异常响应结构
- [x] 健康检查、系统信息、技术栈能力检测、股票池、仪表盘 API
- [x] AKShare 行情数据源适配器（标准化接口，第一阶段不联网启动）
- [x] Vue 3 + Vite + Element Plus 前端骨架
- [x] 平台总览、股票池、系统状态三个页面
- [x] Vue Router、Pinia、Axios 封装，Vite / Nginx API 代理
- [x] 配置模板、Dockerfile、docker-compose、Nginx 配置
- [x] Pytest API 测试与纯函数测试
- [x] README、中文注释、环境变量说明

### 明确不在本阶段

- [ ] 全市场真实行情批量同步任务
- [ ] 因子计算、IC / IR 分析与因子库
- [ ] LightGBM / XGBoost 模型训练与 Optuna 自动调参
- [ ] Backtrader 策略回测、绩效归因和风控
- [ ] 用户体系、权限、实盘交易、消息推送
- [ ] 生产级数据库迁移（Alembic）与任务队列

> 阶段一只交付基础框架。技术栈依赖虽然已声明，但 AI 训练、回测和实时选股功能尚未实现，页面上对应模块明确标记为「待开发」。

---

## 2. 技术栈

| 层级 | 技术 | 作用 |
| --- | --- | --- |
| 后端语言 | Python 3.12 | 服务端与量化研究语言 |
| Web 框架 | FastAPI | REST API、OpenAPI 文档、依赖注入 |
| ASGI Server | Uvicorn | 本地与容器运行 |
| 数据获取 | AKShare | A 股股票与行情数据源适配 |
| 数据处理 | Pandas / NumPy | 行情清洗、计算与向量化 |
| 技术指标 | pandas-ta | 替代 TA-Lib 的纯 Python 指标库 |
| 机器学习 | LightGBM / XGBoost / scikit-learn | 后续选股模型 |
| 超参数优化 | Optuna | 模型参数搜索 |
| 回测 | Backtrader | 后续策略回测 |
| ORM | SQLAlchemy 2.0 | 数据库访问与模型定义 |
| 数据库 | SQLite | 第一阶段零配置存储，可切 PostgreSQL |
| 前端框架 | Vue 3 | 组合式 API + 单文件组件 |
| 构建工具 | Vite 6 | 开发服务器与生产构建 |
| UI 组件 | Element Plus | 表格、表单、抽屉、反馈组件 |
| 状态管理 | Pinia | 后端健康状态共享 |
| HTTP 客户端 | Axios | API 请求与错误统一处理 |
| 容器 | Docker / Nginx | 可选一键部署 |

### 关于 pandas-ta 版本

`pandas-ta 0.4.x` 明确要求 `pandas >= 2.3.2`、`numpy >= 2.2.6`，因此 `requirements.txt` 中对应版本区间已同步调整。若改为 TA-Lib，需要额外安装 TA-Lib C 库，不属于第一阶段默认路径。

---

## 3. 架构总览

```text
┌──────────────────────────────────────────────────────────────┐
│                        Browser                             │
│   Vue 3 + Vite + Element Plus + Pinia + Vue Router         │
└──────────────────────────┬───────────────────────────────────┘
                           │ Axios /api/v1
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI Application                     │
│  API Router → Service → Repository / ORM Adapter            │
│  ├─ health / system / stocks / dashboard                   │
│  ├─ 统一异常处理 + CORS + 请求耗时头                        │
│  └─ OpenAPI / Swagger                                      │
└───────────────┬───────────────────────────┬──────────────────┘
                │                           │
                ▼                           ▼
     ┌────────────────────┐      ┌─────────────────────────┐
     │ SQLAlchemy 2.0     │      │ MarketDataProvider       │
     │ SQLite / PostgreSQL│      │ AKShare Adapter          │
     └────────────────────┘      └─────────────────────────┘
```

设计原则：

1. **路由薄、服务厚**：路由只做参数解析与响应组装，查询/聚合逻辑放在 `services`。
2. **ORM 与 API 契约分离**：数据库模型不等于对外 JSON，所有响应使用 Pydantic schema。
3. **外部数据源可替换**：AKShare 通过 `MarketDataProvider` 抽象隔离。
4. **启动即自检**：应用启动自动建表、写入幂等种子数据、检测依赖能力。
5. **默认安全**：真实 `.env`、数据库文件与密钥不进入版本控制。

---

## 4. 目录结构

```text
AlphaHunter/
├─ backend/                          # Python FastAPI 后端
│  ├─ app/
│  │  ├─ main.py                     # FastAPI 应用工厂、生命周期、中间件
│  │  ├─ api/
│  │  │  ├─ deps.py                  # API 依赖（数据库 Session）
│  │  │  ├─ router.py                # v1 总路由
│  │  │  └─ v1/endpoints/
│  │  │     ├─ health.py             # 健康检查
│  │  │     ├─ system.py             # 系统信息与依赖能力
│  │  │     ├─ stocks.py             # 股票列表 / 筛选项 / 详情
│  │  │     └─ dashboard.py          # 仪表盘聚合
│  │  ├─ core/
│  │  │  ├─ config.py                # Pydantic Settings 配置中心
│  │  │  ├─ logging.py               # 幂等日志初始化
│  │  │  ├─ exceptions.py            # 统一异常与错误响应
│  │  │  └─ capabilities.py          # 技术栈依赖检测
│  │  ├─ db/
│  │  │  ├─ base.py                  # SQLAlchemy DeclarativeBase
│  │  │  ├─ session.py               # Engine / Session / SQLite PRAGMA
│  │  │  ├─ seed.py                  # 幂等演示股票种子
│  │  │  └─ init_db.py               # 建表与初始化 CLI
│  │  ├─ models/
│  │  │  ├─ mixins.py                # 时间戳字段
│  │  │  └─ stock.py                 # Stock / DailyBar
│  │  ├─ schemas/
│  │  │  ├─ common.py                # 分页与错误响应
│  │  │  ├─ stock.py                 # 股票契约
│  │  │  └─ system.py                # 健康/系统/仪表盘契约
│  │  └─ services/
│  │     ├─ stock_service.py         # 股票查询与筛选项聚合
│  │     ├─ dashboard_service.py     # 首页统计
│  │     └─ market_data/
│  │        ├─ base.py               # 数据源抽象与代码分类
│  │        └─ akshare_provider.py   # AKShare 实现
│  ├─ tests/                         # Pytest 测试
│  ├─ data/                          # SQLite 运行目录（.gitkeep）
│  ├─ .env.example                   # 后端配置模板
│  ├─ requirements.txt               # 运行依赖
│  ├─ requirements-dev.txt           # 测试与静态检查依赖
│  ├─ pyproject.toml                 # Pytest / Ruff / Black 配置
│  ├─ Dockerfile
│  └─ .dockerignore
├─ frontend/                         # Vue 3 前端
│  ├─ src/
│  │  ├─ api/                        # Axios 客户端与接口封装
│  │  ├─ components/                 # 可复用展示组件
│  │  ├─ layouts/MainLayout.vue      # 侧边栏 + 顶栏 + 内容区
│  │  ├─ router/index.js             # 路由与页面标题
│  │  ├─ stores/system.js            # Pinia 健康状态
│  │  ├─ styles/index.css            # 设计变量与全局样式
│  │  ├─ utils/format.js             # 日期 / 数字格式化
│  │  ├─ views/                      # 总览、股票池、系统状态
│  │  ├─ App.vue
│  │  └─ main.js
│  ├─ public/favicon.svg
│  ├─ index.html
│  ├─ package.json
│  ├─ pnpm-lock.yaml
│  ├─ pnpm-workspace.yaml
│  ├─ vite.config.js
│  ├─ nginx.conf
│  ├─ Dockerfile
│  ├─ .env.example
│  └─ .dockerignore
├─ docker-compose.yml                # 前后端一键编排
├─ .gitignore
├─ .editorconfig
├─ .dockerignore
└─ README.md
```

---

## 5. 快速启动

### 5.1 环境要求

- Python **3.12**
- Node.js **20+**（推荐 22）
- pnpm **11+**（项目使用 `allowBuilds` 放行 esbuild / vue-demi 的构建脚本）
- Docker Desktop（可选，仅容器启动时需要）

### 5.2 启动后端

```bash
cd backend
```

**Windows PowerShell：**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env   # 可选，不复制则使用默认配置
python -m app.db.init_db      # 可选：应用启动时也会自动初始化
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

如 PowerShell 禁止执行脚本，可只对当前进程放行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**macOS / Linux / Git Bash：**

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Git Bash: source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env                # 可选
python -m app.db.init_db            # 可选
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

后端启动后：

- API：<http://127.0.0.1:8000>
- Swagger：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>
- 健康检查：<http://127.0.0.1:8000/api/v1/health>

### 5.3 启动前端

另开一个终端：

```bash
cd frontend
pnpm install
pnpm dev
```

打开 <http://localhost:5173>。Vite 会把 `/api`、`/docs`、`/openapi.json` 代理到 `http://127.0.0.1:8000`。

生产构建：

```bash
pnpm build
pnpm preview
```

### 5.4 一键容器启动（可选）

需要 Docker Desktop 已运行：

```bash
docker compose up --build
```

- 前端：<http://localhost:5173>
- 后端：<http://localhost:8000/docs>
- SQLite 数据保存在命名卷 `alphahunter-data`

停止服务：

```bash
docker compose down
```

> 当前开发环境未安装 Docker，Docker 配置已提供但未在本机实际构建验证。

---

## 6. 验证方式

### 6.1 后端测试

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest
```

测试使用独立的临时 SQLite 数据库，不会污染 `backend/data/alphahunter.db`。覆盖：

- 根路径与健康检查
- 股票分页、关键词搜索、交易所过滤
- 筛选项与单票详情
- 统一 404 / 422 错误结构
- 系统依赖矩阵与仪表盘真实计数
- 证券代码规范化与板块分类

### 6.2 前端构建

```bash
cd frontend
pnpm build
```

构建产物输出到 `frontend/dist`。

### 6.3 手工 API 验证

```bash
curl http://127.0.0.1:8000/api/v1/health
curl "http://127.0.0.1:8000/api/v1/stocks?page=1&page_size=5"
curl http://127.0.0.1:8000/api/v1/stocks/600519
curl http://127.0.0.1:8000/api/v1/stocks/filters
curl http://127.0.0.1:8000/api/v1/dashboard/summary
curl http://127.0.0.1:8000/api/v1/system/info
```

---

## 7. 配置说明

后端配置全部带 `ALPHAHUNTER_` 前缀，优先从环境变量读取，其次读取 `backend/.env`。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `ALPHAHUNTER_ENVIRONMENT` | `development` | development / testing / production |
| `ALPHAHUNTER_DEBUG` | `true` | 生产环境应设为 false |
| `ALPHAHUNTER_HOST` | `127.0.0.1` | `python -m app.main` 使用 |
| `ALPHAHUNTER_PORT` | `8000` | 服务端口 |
| `ALPHAHUNTER_API_V1_PREFIX` | `/api/v1` | API 前缀 |
| `ALPHAHUNTER_SECRET_KEY` | 占位值 | 生产必须替换 |
| `ALPHAHUNTER_DATABASE_URL` | `sqlite:///.../data/alphahunter.db` | 数据库连接串 |
| `ALPHAHUNTER_SQL_ECHO` | `false` | 是否打印 SQL |
| `ALPHAHUNTER_SEED_DEMO_DATA` | `true` | 初始化时写入演示股票 |
| `ALPHAHUNTER_CORS_ORIGINS` | 本地 5173 两个地址 | 逗号分隔的跨域白名单 |
| `ALPHAHUNTER_LOG_LEVEL` | `INFO` | 日志级别 |
| `ALPHAHUNTER_MARKET_DATA_TIMEOUT` | `30` | 外部行情请求超时（预留） |

前端配置：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `VITE_API_BASE_URL` | `/api/v1` | 浏览器请求的 API 基础路径 |
| `VITE_PROXY_TARGET` | `http://127.0.0.1:8000` | Vite 开发代理目标 |

> `.env` 已加入 `.gitignore`。不要提交真实密钥。

---

## 8. API 一览

所有接口前缀为 `/api/v1`，完整 schema 见 Swagger。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 健康检查，真实执行 `SELECT 1` |
| GET | `/system/info` | 应用信息、Python 版本、数据库、依赖矩阵 |
| GET | `/stocks` | 分页股票列表，支持 `page/page_size/keyword/exchange` |
| GET | `/stocks/filters` | 数据库聚合的交易所与行业筛选项 |
| GET | `/stocks/{symbol}` | 6 位证券代码详情 |
| GET | `/dashboard/summary` | 股票数、行情数、数据状态、依赖就绪度 |

统一错误响应：

```json
{
  "code": "STOCK_NOT_FOUND",
  "message": "未找到代码为 999999 的股票",
  "details": { "symbol": "999999" }
}
```

---

## 9. 数据库

### 9.1 表结构

`stocks`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | INTEGER PK | 自增主键 |
| `symbol` | VARCHAR(10) UNIQUE | 6 位证券代码 |
| `name` | VARCHAR(50) | 证券简称 |
| `exchange` | VARCHAR(10) | SSE / SZSE / BSE |
| `market` | VARCHAR(20) | 主板 / 创业板 / 科创板 / 北交所 |
| `industry` | VARCHAR(64) | 行业 |
| `list_date` | DATE | 上市日期 |
| `is_active` | BOOLEAN | 是否正常上市 |
| `data_source` | VARCHAR(20) | demo / akshare / manual |
| `description` | TEXT | 备注 |
| `created_at` / `updated_at` | DATETIME | 审计时间 |

`daily_bars`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | INTEGER PK | 自增主键 |
| `symbol` | FK → stocks.symbol | 证券代码，级联删除 |
| `trade_date` | DATE | 交易日 |
| `open/high/low/close` | FLOAT | 前复权 OHLC |
| `volume` / `amount` | FLOAT | 成交量 / 成交额 |
| `pct_change` | FLOAT | 涨跌幅 |
| `turnover_rate` | FLOAT | 换手率 |
| `created_at` / `updated_at` | DATETIME | 审计时间 |

唯一约束：`(symbol, trade_date)`，防止重复同步。

### 9.2 初始化命令

```bash
cd backend
python -m app.db.init_db
python -m app.db.init_db --no-seed   # 只建表，不写入演示股票
```

数据库文件默认位于 `backend/data/alphahunter.db`，已被 Git 忽略。

### 9.3 切换到 PostgreSQL

1. 安装驱动：`pip install "psycopg[binary]"`。
2. 配置连接串：

```env
ALPHAHUNTER_DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/alphahunter
```

3. 重新执行初始化。ORM 与查询代码无需修改。

> 当表结构开始频繁演进时，第二阶段应引入 Alembic 迁移；阶段一使用 `create_all` 保持零配置。

---

## 10. AKShare 适配器

`app/services/market_data/` 通过抽象接口隔离数据源：

```python
class MarketDataProvider(ABC):
    def fetch_stock_list(self) -> list[StockRecord]: ...
    def fetch_daily_bars(self, symbol, start_date, end_date, adjust="qfq") -> list[DailyBarRecord]: ...
```

已实现：

- `normalize_symbol`：兼容 `600519`、`600519.SH`、`sh600519`
- `classify_a_share`：按代码段识别上交所/深交所/北交所与板块
- `AkshareMarketDataProvider.fetch_stock_list()`：调用 `stock_info_a_code_name()`
- `AkshareMarketDataProvider.fetch_daily_bars()`：调用 `stock_zh_a_hist()`，统一中文列名并处理 NaN

阶段一**不会在应用启动时联网**。`AKShare` 未安装或接口异常时，健康检查与股票查询仍然可用；真正调用行情方法时会抛出统一 `DataProviderError`。第二批将增加「同步任务 + 增量更新 + 数据质量校验」。

---

## 11. 前端页面

| 路由 | 页面 | 内容 |
| --- | --- | --- |
| `/` | 平台总览 | 阶段定位、真实统计、研究流水线、数据状态、股票预览 |
| `/stocks` | 股票池 | 分页表格、关键词/交易所筛选、详情抽屉 |
| `/system` | 系统状态 | 运行环境、依赖矩阵、API 清单、架构说明 |

页面遵循：

- 桌面端固定侧边栏，移动端切换为抽屉导航；
- API 不可达时显示明确错误提示，不伪造数据；
- 所有后端字段通过 API 获取，前端不硬编码股票列表；
- 未实现的 AI、因子、回测模块明确标记「待开发」。

---

## 12. 文件职责清单

### 根目录

| 文件 | 作用 |
| --- | --- |
| `.gitignore` | 忽略虚拟环境、数据库、密钥、构建产物与缓存 |
| `.editorconfig` | 统一 UTF-8、LF、缩进和行宽 |
| `.dockerignore` | 根 Docker 构建上下文排除项 |
| `docker-compose.yml` | 后端 + 前端 + SQLite 数据卷编排 |
| `README.md` | 项目说明、启动、配置、架构与 API 文档 |

### 后端

| 文件 | 作用 |
| --- | --- |
| `backend/.env.example` | 后端环境变量模板 |
| `backend/requirements.txt` | 运行依赖（FastAPI、AKShare、ML、回测） |
| `backend/requirements-dev.txt` | 测试与 Ruff 依赖 |
| `backend/pyproject.toml` | Pytest、Ruff、Black 工程配置 |
| `backend/Dockerfile` | Python 3.12 后端镜像与健康检查 |
| `backend/.dockerignore` | 后端镜像构建排除项 |
| `backend/app/__init__.py` | 后端包标识与版本 |
| `backend/app/main.py` | 应用工厂、生命周期、CORS、耗时中间件 |
| `backend/app/core/config.py` | Pydantic Settings 配置中心与脱敏 |
| `backend/app/core/logging.py` | 幂等日志初始化 |
| `backend/app/core/exceptions.py` | 业务异常、HTTP 异常、校验异常、兜底异常处理 |
| `backend/app/core/capabilities.py` | 按组检测技术栈依赖与版本 |
| `backend/app/db/base.py` | SQLAlchemy 声明基类 |
| `backend/app/db/session.py` | Engine、Session、SQLite 外键/WAL PRAGMA |
| `backend/app/db/seed.py` | 8 只演示股票的幂等种子 |
| `backend/app/db/init_db.py` | 建表、写入种子、CLI 入口 |
| `backend/app/models/mixins.py` | created_at / updated_at 通用字段 |
| `backend/app/models/stock.py` | Stock 与 DailyBar ORM 模型 |
| `backend/app/schemas/common.py` | 泛型分页、错误、消息响应 |
| `backend/app/schemas/stock.py` | 股票与筛选器的 Pydantic 契约 |
| `backend/app/schemas/system.py` | 健康、系统、仪表盘契约 |
| `backend/app/api/deps.py` | 数据库 Session 依赖 |
| `backend/app/api/router.py` | v1 总路由挂载 |
| `backend/app/api/v1/endpoints/health.py` | 健康检查接口 |
| `backend/app/api/v1/endpoints/system.py` | 系统信息与依赖矩阵接口 |
| `backend/app/api/v1/endpoints/stocks.py` | 股票分页、筛选、详情接口 |
| `backend/app/api/v1/endpoints/dashboard.py` | 仪表盘聚合接口 |
| `backend/app/services/stock_service.py` | 股票查询与筛选项聚合 |
| `backend/app/services/dashboard_service.py` | 首页统计与数据状态判断 |
| `backend/app/services/market_data/base.py` | 数据源抽象、记录对象、代码分类 |
| `backend/app/services/market_data/akshare_provider.py` | AKShare 股票列表与日行情适配 |
| `backend/tests/conftest.py` | 独立临时数据库与 TestClient 夹具 |
| `backend/tests/test_health.py` | 根路径与健康检查测试 |
| `backend/tests/test_stocks.py` | 股票 API 与错误结构测试 |
| `backend/tests/test_system.py` | 系统信息与仪表盘测试 |
| `backend/tests/test_market_data.py` | 代码规范化与板块分类测试 |
| `backend/data/.gitkeep` | 保留数据目录，忽略实际数据库文件 |

### 前端

| 文件 | 作用 |
| --- | --- |
| `frontend/package.json` | 依赖与 dev/build/preview 脚本、pnpm 版本 |
| `frontend/pnpm-lock.yaml` | 锁定前端依赖解析结果 |
| `frontend/pnpm-workspace.yaml` | pnpm 工作区与 esbuild/vue-demi 构建白名单 |
| `frontend/vite.config.js` | Vue 插件、`@` 别名、API 代理、代码分割 |
| `frontend/index.html` | HTML 入口与首屏 loading 占位 |
| `frontend/src/main.js` | 应用初始化（Pinia / Router / Element Plus） |
| `frontend/src/App.vue` | 根路由出口 |
| `frontend/src/router/index.js` | 嵌套路由、懒加载、页面标题 |
| `frontend/src/api/client.js` | Axios 实例、响应解包、中文错误提示 |
| `frontend/src/api/system.js` | 健康、系统信息、仪表盘请求 |
| `frontend/src/api/stocks.js` | 股票列表、筛选项、详情请求 |
| `frontend/src/stores/system.js` | Pinia 后端健康状态 |
| `frontend/src/layouts/MainLayout.vue` | 侧边栏、顶栏、状态指示、移动端导航 |
| `frontend/src/views/DashboardView.vue` | 平台总览页 |
| `frontend/src/views/StocksView.vue` | 股票池列表与详情抽屉 |
| `frontend/src/views/SystemView.vue` | 系统状态与依赖矩阵 |
| `frontend/src/components/StatCard.vue` | 指标卡片组件 |
| `frontend/src/styles/index.css` | 设计变量、Element Plus 主题、全局样式 |
| `frontend/src/utils/format.js` | 日期、数字、运行时长、交易所格式化 |
| `frontend/public/favicon.svg` | 品牌 favicon |
| `frontend/nginx.conf` | SPA 回退、API/文档代理、gzip |
| `frontend/Dockerfile` | Node 构建 + Nginx 运行的多阶段镜像 |
| `frontend/.env.example` | 前端环境变量模板 |
| `frontend/.dockerignore` | 前端镜像构建排除项 |

---

## 13. 开发规范

- Python 使用 4 空格、行宽 100、类型注解优先。
- API 响应必须通过 Pydantic schema，不直接返回 ORM 对象。
- 新业务逻辑放在 `services`，不要在路由中写复杂查询。
- 所有外部数据源必须实现 `MarketDataProvider`，便于替换和测试。
- 前端页面不硬编码后端数据，统一通过 `src/api` 请求。
- 真实密钥、数据库与日志不得提交。
- 代码注释使用中文，说明「为什么」而不只是「做了什么」。

静态检查：

```bash
cd backend
.\.venv\Scripts\python.exe -m ruff check app tests
```

---

## 14. 第二阶段路线

1. **数据同步**：AKShare 全市场股票列表 + 日线增量同步，加入任务状态、失败重试和数据质量校验。
2. **数据库迁移**：引入 Alembic，把 `create_all` 升级为可回滚迁移。
3. **因子研究**：pandas-ta 指标、因子标准化、IC / Rank IC、分层回测。
4. **AI 选股**：LightGBM / XGBoost 训练管线，Optuna 调参，模型版本管理。
5. **策略回测**：Backtrader 策略、交易成本、滑点、绩效归因。
6. **平台增强**：认证、任务队列、缓存、监控、PostgreSQL 与对象存储。

---

## 15. 常见问题

**Q：`uvicorn` 找不到？**
A：确认虚拟环境已激活，或在 backend 目录使用 `.venv/Scripts/python.exe -m uvicorn app.main:app --reload`。

**Q：前端请求 404 / 502？**
A：确认后端运行在 `127.0.0.1:8000`，并检查 `VITE_PROXY_TARGET`。生产容器中由 Nginx 代理到 `backend:8000`。

**Q：为什么没有 TA-Lib？**
A：第一阶段选择 pandas-ta，避免 TA-Lib C 库在不同系统的编译成本。后续有性能需求时可替换实现。

**Q：数据库在哪里？**
A：默认在 `backend/data/alphahunter.db`。删除该文件后重新启动即可重建；生产环境请使用持久化卷或 PostgreSQL。

**Q：为什么页面显示「演示数据」？**
A：阶段一只有股票静态种子，尚未同步真实行情。接入 AKShare 日线后，数据状态会转为 `ready`。

---

## 16. 免责声明

本项目提供的所有数据、代码与界面仅用于技术研究和教学演示，不构成投资建议、收益承诺或交易依据。A 股市场存在显著风险，任何策略在实盘使用前都必须经过充分回测、压力测试与合规审查。
