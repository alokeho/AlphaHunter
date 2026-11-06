"""AlphaHunter 后端应用包。

本包承载 A 股 AI 量化选股平台的后端服务。第一阶段只实现：
- FastAPI 应用骨架与统一异常处理
- SQLAlchemy + SQLite 数据层与初始化脚本
- 股票基础资料查询接口
- AKShare 数据源适配器骨架
- 运行环境与依赖能力自检
"""

__version__ = "0.1.0"
