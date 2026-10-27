from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from tools import ToolCall, execute_tool, load_guides, markdown_to_html


load_dotenv(Path(__file__).parent / ".env")

st.set_page_config(page_title="校园办事指南助手", page_icon="▣", layout="wide")

st.markdown(
    """
    <style>
    :root { --ink:#17212b; --muted:#5d6c76; --teal:#0b6e69; --deep:#123f43; --mint:#e8f4f1; --line:#d5e2de; --gold:#e6c36a; }
    .stApp { background: #f7f8f5; color: var(--ink); }
    .block-container { max-width: 1220px; padding-top: 2.2rem; }
    h1,h2,h3 { color: var(--ink); letter-spacing: 0; }
    .hero { background: var(--deep); color: #f6faf7; padding: 34px 38px; border-radius: 16px; margin-bottom: 26px; box-shadow: 0 12px 28px rgba(18,63,67,.13); }
    .hero h1 { color: #f6faf7; margin: 0 0 10px; font-size: 2.35rem; letter-spacing: -.02em; }
    .hero p { margin: 0; color: #d8e9e5; max-width: 720px; line-height: 1.65; }
    .guide-title { font-size: 1.35rem; font-weight: 750; color: var(--teal); margin-bottom: 6px; }
    .catalog { border-top: 1px solid var(--line); }
    .catalog-item { padding: 13px 0 12px; border-bottom: 1px solid var(--line); }
    .catalog-item strong { color: var(--ink); font-size: .98rem; }
    .catalog-item span { display:block; color: var(--muted); font-size: .82rem; margin-top: 4px; line-height: 1.45; }
    .catalog-category { color: var(--teal); font-size: .75rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
    .muted { color: var(--muted); }
    .stButton>button { border-radius: 9px; min-height: 2.8rem; font-weight: 650; }
    .stTextArea textarea { border-radius: 10px; border-color: #b9d8d1; }
    </style>
    <div class='hero'><h1>校园办事指南助手</h1><p>描述你要办理的校园事务，助手会整理办理步骤、所需材料和可下载的任务清单。</p></div>
    """,
    unsafe_allow_html=True,
)


def model_run(user_text: str) -> tuple[list[ToolCall], list[Any]] | None:
    """Run a real multi-turn OpenAI-compatible tool-calling loop."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL"))
        tools = [
            {"type": "function", "function": {"name": "search_guides", "description": "搜索校园办事指南", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
            {"type": "function", "function": {"name": "get_requirements", "description": "查询指南步骤和材料", "parameters": {"type": "object", "properties": {"guide_id": {"type": "string"}}, "required": ["guide_id"]}}},
            {"type": "function", "function": {"name": "build_checklist", "description": "生成办事清单", "parameters": {"type": "object", "properties": {"guide_id": {"type": "string"}, "student_context": {"type": "string"}}, "required": ["guide_id"]}}},
        ]
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "qwen-plus"),
            messages=[{"role": "system", "content": "你是校园办事助手。只通过提供的工具获取信息，必要时依次调用搜索、详情和清单工具。"}, {"role": "user", "content": user_text}],
            tools=tools,
            tool_choice="auto",
        )
        messages = [
            {"role": "system", "content": "你是校园办事助手。只通过提供的工具获取信息，必要时依次调用搜索、详情和清单工具。"},
            {"role": "user", "content": user_text},
        ]
        calls: list[ToolCall] = []
        results: list[Any] = []
        for _ in range(4):
            tool_calls = response.choices[0].message.tool_calls or []
            if not tool_calls:
                break
            assistant_message = {"role": "assistant", "content": response.choices[0].message.content, "tool_calls": []}
            for tool_call in tool_calls:
                assistant_message["tool_calls"].append({"id": tool_call.id, "type": "function", "function": {"name": tool_call.function.name, "arguments": tool_call.function.arguments}})
            messages.append(assistant_message)
            for tool_call in tool_calls:
                call = ToolCall(tool_call.function.name, json.loads(tool_call.function.arguments))
                result = execute_tool(call)
                calls.append(call)
                results.append(result)
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result, ensure_ascii=False)})
            response = client.chat.completions.create(model=os.getenv("OPENAI_MODEL", "qwen-plus"), messages=messages, tools=tools, tool_choice="auto")
        return calls, results
    except Exception:
        return None


def render_result(calls: list[ToolCall], results: list[Any]) -> None:
    st.subheader("办理结果")
    guide = next((result for call, result in zip(calls, results) if call.name == "get_requirements" and result), None)
    if guide:
        st.markdown(f"<div class='guide-title'>{guide['title']}</div>", unsafe_allow_html=True)
        st.write(guide["summary"])
        left, right = st.columns(2)
        with left:
            st.markdown("**办理步骤**")
            for index, step in enumerate(guide["steps"], 1):
                st.write(f"{index}. {step}")
        with right:
            st.markdown("**所需材料**")
            for material in guide["materials"]:
                st.write(f"□ {material}")
            st.caption(f"办理部门：{guide['department']} · 地点：{guide['location']}")
            st.info(guide["official_note"])
    checklist = next((result for call, result in zip(calls, results) if call.name == "build_checklist" and result), None)
    if checklist:
        st.download_button("下载 Markdown 办事清单", checklist, file_name="campus-checklist.md", mime="text/markdown")
        st.download_button("下载 HTML 办事清单", markdown_to_html(checklist), file_name="campus-checklist.html", mime="text/html")
        with st.expander("查看生成的清单"):
            st.code(checklist, language="markdown")
    if guide:
        st.markdown("**模拟提交（仅本地演示，不会发送到真实系统）**")
        confirmed = st.checkbox("我确认创建一条本地模拟申请", key=f"confirm_{guide['id']}")
        if st.button("提交模拟申请", key=f"submit_{guide['id']}"):
            if not confirmed:
                st.warning("请先勾选确认框，系统不会在未确认时提交。")
            else:
                submission = execute_tool(ToolCall("submit_application", {"guide_id": guide["id"], "student_context": "课堂演示", "confirmed": True}))
                st.success(f"模拟申请已创建：{submission['reference']}（{submission['status']}）")


if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown("### 演示控制台")
    st.success("真实模型模式")
    st.caption("当前通过 Ollama 调用 qwen2.5:7b，并使用 Tool Calling 执行业务操作。")
    st.markdown("---")
    st.markdown("**推荐演示话术**")
    st.code("我想办理校园卡挂失补办，需要准备什么？", language="text")
    st.code("宿舍水龙头坏了，报修流程和材料是什么？", language="text")
    st.caption("示例数据仅用于课程演示；真实办理请以学校最新公告为准。")

left, right = st.columns([1.1, 0.9], gap="large")
with left:
    st.subheader("输入你的校园事务")
    prompt = st.text_area("问题", placeholder="例如：我想请病假，需要哪些步骤和材料？", height=120, label_visibility="collapsed")
    run = st.button("开始办理", type="primary", use_container_width=True)
    if run:
        if not prompt.strip():
            st.warning("请先输入一个校园事务问题。")
        else:
            model_result = model_run(prompt)
            if model_result and model_result[0]:
                calls, results = model_result
            else:
                st.error("模型没有返回工具调用。请确认 Ollama 正在运行，并检查 .env 中的模型配置。")
                calls, results = [], []
            st.session_state.history.append({"prompt": prompt, "calls": calls, "results": results})
            render_result(calls, results)
    elif st.session_state.history:
        latest = st.session_state.history[-1]
        render_result(latest["calls"], latest["results"])

with right:
    st.subheader("可查询事项")
    st.caption("当前指南库支持以下校园服务，直接用自然语言提问即可。")
    catalog_html = ["<div class='catalog'>"]
    for guide in load_guides():
        catalog_html.append(
            f"<div class='catalog-item'><div class='catalog-category'>{guide['category']}</div>"
            f"<strong>{guide['title']}</strong><span>{guide['summary']}</span></div>"
        )
    catalog_html.append("</div>")
    st.markdown("".join(catalog_html), unsafe_allow_html=True)
