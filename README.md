# Claude API Agentic Bridge (V4.0)

A powerful FastAPI-based bridge that transforms Claude 3.5 Sonnet (Web) into a fully functional Agentic model. 

[English](#english) | [中文说明](#chinese)

---

<a name="english"></a>
## Features (English)
- **Agentic Orchestration (V4.0)**: Automatically generates bash commands to fetch real system data, overcoming Claude's compliance refusals and "no access" hallucinations.
- **OpenAI Compatible**: Seamlessly integrates with tools like Hermes Agent, OpenAI SDKs, and more.
- **Smart Filtering**: Intercepts and replaces AI refusal messages with factual execution results.
- **Non-stream Support**: Specifically optimized for "Auxiliary title generation" in chat interfaces.

---

<a name="chinese"></a>
## 功能特性 (Chinese)
- **V4.0 代理化调度 (Agentic Orchestration)**：自动诱导模型生成 bash 指令获取真实系统数据。彻底解决 Claude 3.5 Sonnet 在 Web 环境下常见的“无权限”、“路径不存在”等合规性阻断和幻觉问题。
- **OpenAI 协议兼容**：完美适配 Hermes Agent、OpenAI SDK 以及各类支持 OpenAI 格式的客户端。
- **智能过滤机制**：实时拦截 AI 的身份声明及拒答词，确保回复中只包含有效的事实和执行结果。
- **非流式请求优化**：专门针对聊天界面的“辅助标题生成”进行了优化，支持标准的 JSON 响应格式。

## 快速开始
1. 克隆仓库。
2. 安装依赖：`pip install -r requirements-extra.txt`。
3. 在 `accounts.json` 中配置您的 `session_key`。
4. 启动服务：`python api_server.py`。

## 许可证
MIT
