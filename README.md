# 校园办事指南助手

一个面向学生的路径 B 项目：用户用自然语言描述校园事务，Agent 通过 Tool Calling 搜索本地指南、读取步骤与材料，并生成可下载的 Markdown/HTML 办事清单。

## 项目亮点

- 4 个可调用业务工具：`search_guides`、`get_requirements`、`build_checklist`、`submit_application`
- Streamlit 交互界面，右侧展示实际工具调用链
- 使用真实模型进行多轮 Tool Calling
- 支持 Ollama 本地模型和其他 OpenAI 兼容接口
- 模拟提交必须经过用户确认，且不会连接真实学校系统
- 数据、工具、界面分层，便于现场解释关键代码

## 环境要求

- Windows 10/11
- Python 3.10+

## 安装与启动（Windows PowerShell）

```powershell
cd W
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
python -m streamlit run app.py
```

如果你把仓库克隆到了其他目录，请把第一行 `cd W` 换成实际仓库路径。启动前请确保 Ollama 服务正在运行，或在 `.env` 中填写其他 OpenAI 兼容服务配置。浏览器打开 `http://127.0.0.1:8501`。

## 换电脑演示

PPT 不需要安装 Python，直接双击 `slides.html`，或双击 `open_slides.bat` 即可打开。

如果使用 GitHub Pages，打开站点首页即可看到项目入口，再点击“打开项目 PPT”。GitHub 仓库的代码页面只会显示 `.bat` 和 `.py` 文件内容，不会自动执行应用。

应用需要在演示电脑上安装 Python 和 Ollama。Windows 用户可以双击 `run_app.bat`，脚本会创建虚拟环境、安装依赖、检查并启动 `qwen2.5:7b`，然后打开 Streamlit 应用。首次运行需要下载约 4.7 GB 模型。

## 可选模型配置

默认配置使用 Ollama 的 `qwen2.5:7b`：

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=qwen2.5:7b
```

也可以在 `.env` 中填写其他 OpenAI 兼容服务的 Key、Base URL 和模型名。不要把真实 `.env` 提交到 Git。

## 推荐演示话术

1. “我想办理校园卡挂失补办，需要准备什么？”
2. “宿舍水龙头坏了，报修流程和材料是什么？”
3. “我想请病假，请生成一份办理清单。”

## 关键代码讲解

- `tools.py`：三个业务工具和 `TOOL_REGISTRY`，负责可审计的本地业务操作。
- `app.py:model_run`：执行多轮 Tool Calling，把工具结果继续交给模型，直到主路径结束。
- `app.py:render_result`：将工具结果转成步骤、材料和下载文件。

## 相比课堂 demo 的增量

本项目不是单轮聊天换皮：新增了校园办事场景、本地结构化指南数据、四个业务工具、可见执行日志、办事清单文件产出，以及确认后模拟提交。

## 数据与合规说明

项目中的指南是课程演示用虚构数据，不包含真实学生个人信息。真实办理时应以学校官方最新文件为准；涉及个人信息时只使用虚构样例。

---

# W

HarmonyOS ArkUI demo for a wrong-answer cause knowledge base.

## Use in DevEco Studio

Create an Empty Ability project, then copy `Index.ets` to
`entry/src/main/ets/pages/Index.ets` (replacing the generated page). Run the
project on a HarmonyOS virtual device. This demo uses in-memory sample data;
entries are not persisted after the app process exits.
