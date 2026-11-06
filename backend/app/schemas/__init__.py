"""Pydantic 数据契约包。

Schemas 负责 API 输入输出结构，与 ORM 模型解耦：
- ORM 变更不会自动改变对外契约；
- 可以显式控制字段是否暴露、是否可写；
- 为前端 TypeScript/JavaScript 消费提供稳定的 JSON 结构。
"""
