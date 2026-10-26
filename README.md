# 校园办事指南助手

一个面向学生的路径 B 项目：用户用自然语言描述校园事务，Agent 通过 Tool Calling 搜索本地指南、读取步骤与材料，并生成可下载的 Markdown/HTML 办事清单。

## 项目亮点

- 4 个可调用业务工具：`search_guides`、`get_requirements`、`build_checklist`、`submit_application`
- Streamlit 交互界面，右侧展示实际工具调用链
- 本地演示模式无需 API Key，适合课堂现场稳定演示
- 可选 OpenAI 兼容接口（例如阿里百炼）
- 模拟提交必须经过用户确认，且不会连接真实学校系统
- 数据、工具、界面分层，便于现场解释关键代码

## 环境要求

- Windows 10/11
- Python 3.10+

## 安装与启动（Windows PowerShell）

```powershell
cd outputs\campus-guide-assistant
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

浏览器打开 Streamlit 输出的本地地址即可。`.env` 可以保持空白，项目会自动使用本地演示模式。

## 可选模型配置

在 `.env` 中填写 OpenAI 兼容服务的 Key、Base URL 和模型名。不要把真实 `.env` 提交到 Git。没有 Key 时，项目仍可完整演示工具调用闭环。

## 推荐演示话术

1. “我想办理校园卡挂失补办，需要准备什么？”
2. “宿舍水龙头坏了，报修流程和材料是什么？”
3. “我想请病假，请生成一份办理清单。”

## 关键代码讲解

- `tools.py`：三个业务工具和 `TOOL_REGISTRY`，负责可审计的本地业务操作。
- `app.py:local_plan`：本地演示模式生成 `ToolCall` 序列，确保没有 Key 也能现场运行。
- `app.py:model_run`：执行多轮 Tool Calling，把工具结果继续交给模型，直到主路径结束。
- `app.py:render_result`：将工具结果转成步骤、材料和下载文件。

## 相比课堂 demo 的增量

本项目不是单轮聊天换皮：新增了校园办事场景、本地结构化指南数据、四个业务工具、可见执行日志、办事清单文件产出、确认后模拟提交，以及模型不可用时的本地演示降级方案。

## 数据与合规说明

项目中的指南是课程演示用虚构数据，不包含真实学生个人信息。真实办理时应以学校官方最新文件为准；涉及个人信息时只使用虚构样例。
