# 校园办事指南助手

这是一个面向学生的路径 B 智能体应用。用户用自然语言描述校园事务，真实模型负责理解需求并选择工具，程序再从结构化指南中读取信息，返回办理步骤、所需材料和可下载的办事清单。

## 一、项目功能

- 使用 Ollama 本地运行 `qwen2.5:7b`。
- 支持自然语言到 Tool Calling 的完整流程。
- 支持 8 类校园事项：请假、借阅证补办、校园卡补办、宿舍报修、证明打印、校园网服务、奖助学金申请、失物招领。
- 生成 Markdown 和 HTML 两种办事清单。
- 模拟提交需要用户明确勾选确认，只生成本地演示编号，不访问真实学校系统。
- 使用 Streamlit 提供可交互网页界面。

## 二、项目文件

| 文件 | 作用 |
| --- | --- |
| `app.py` | 应用入口，负责页面、模型请求、Tool Calling 和结果展示。 |
| `tools.py` | 业务工具、工具注册表、工具分发和提交确认检查。 |
| `data/guides.json` | 结构化校园指南数据。 |
| `requirements.txt` | Python 依赖列表。 |
| `.env.example` | 模型配置示例，不包含真实密钥。 |
| `slides.html` | 期末项目 PPT，浏览器可以直接打开。 |
| `启动校园助手.bat` | Windows 一键启动脚本，双击后自动准备环境并打开应用。 |

## 三、运行应用

### 环境要求

- Windows 10 或 Windows 11
- Python 3.10 或更高版本
- Ollama
- 至少约 5 GB 可用磁盘空间，用于模型文件

### 方法一：PowerShell 一次启动

下载并解压整个仓库后，在 PowerShell 中复制下面的完整代码。只需要修改第一行的项目路径：

```powershell
$project = "C:\Users\51600\Documents\Codex\2026-10-26\new-chat\outputs\campus-guide-assistant"
Set-Location $project
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "未找到 Python，请先安装 Python 3.10 或更高版本。" }
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { throw "未找到 Ollama，请先安装 Ollama。" }
if (-not (Test-Path ".venv\Scripts\python.exe")) { python -m venv .venv }
& ".venv\Scripts\python.exe" -m pip install -r requirements.txt
$model = ollama list 2>$null | Select-String "qwen2.5:7b"
if (-not $model) { ollama pull qwen2.5:7b }
$port = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
if ($port) {
    Start-Process "http://127.0.0.1:8501"
    Write-Host "应用已经在运行，已打开 http://127.0.0.1:8501"
} else {
    Start-Process "http://127.0.0.1:8501"
    & ".venv\Scripts\python.exe" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
}
```

首次运行会创建虚拟环境、安装依赖，并下载约 4.7 GB 的 `qwen2.5:7b` 模型。以后再次运行会直接启动应用。

应用地址：

```text
http://127.0.0.1:8501
```

如果提示 `Port 8501 is not available`，说明应用已经运行，直接打开上面的地址即可，不要重复启动。

### 方法二：双击启动

也可以直接双击项目根目录中的 `启动校园助手.bat`。这个文件已经包含在仓库中，不需要单独下载；它会自动创建虚拟环境、安装依赖、准备模型并启动应用。

## 四、模型配置

项目默认连接本机 Ollama，不需要云端 API Token。`.env` 可以写成：

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=qwen2.5:7b
```

如果使用其他 OpenAI 兼容服务，可以替换接口地址、模型名称和密钥。真实 `.env` 不要提交到公开仓库。

## 五、一次请求如何执行

以“我想办理校园卡挂失补办，需要准备什么？”为例：

1. Streamlit 接收用户输入。
2. Qwen2.5 根据工具描述选择 `search_guides`。
3. 程序在 `guides.json` 中匹配校园卡指南。
4. 程序调用 `get_requirements` 读取步骤、材料、部门和地点。
5. 用户表达需要材料或清单时，程序调用 `build_checklist`。
6. 页面展示办理结果，并提供 Markdown 和 HTML 下载。

如果本地模型只返回搜索工具，程序会根据模型选择的指南自动补齐详情和清单步骤，保证页面能够显示完整结果。

## 六、关键代码

- `tools.py` 的 `TOOL_REGISTRY`：工具白名单，限制模型只能调用已注册业务函数。
- `tools.py` 的 `execute_tool`：按工具名称分发调用，并拒绝未知工具。
- `app.py` 的 `model_run`：创建 OpenAI 兼容客户端，向模型发送工具定义，执行多轮 Tool Calling。
- `app.py` 的 `render_result`：把工具结果渲染为步骤、材料、提示和下载按钮。
- `tools.py` 的 `submit_application`：检查 `confirmed` 参数，保护有状态变化的模拟操作。

## 七、现场演示建议

1. 打开应用首页。
2. 输入“我想办理校园卡挂失补办，需要准备什么？”。
3. 等待本地 7B 模型完成推理，首次响应可能需要 20 至 30 秒。
4. 展示步骤、材料、办理部门和地点。
5. 下载 HTML 清单。
6. 点击模拟提交但不勾选确认框，展示系统拒绝未授权操作。
7. 勾选确认后再次提交，展示本地模拟编号。

## 八、数据说明

项目中的校园指南和个人信息均为课程演示样例，不代表任何学校的真实规定。真实办理时应以学校官方最新通知为准，不要在演示中填写真实账号、密码、手机号或宿舍信息。

## 九、项目演示材料

### PPT

[校园办事指南助手期末项目 PPT](slides.html)

### 核心文件

- [校园办事指南助手应用代码](app.py)
- [业务工具代码](tools.py)
- [校园事项数据](data/guides.json)
