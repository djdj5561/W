from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from tools import ToolCall, execute_tool, markdown_to_html, search_guides


load_dotenv(Path(__file__).parent / ".env")

st.set_page_config(page_title="校园办事指南助手", page_icon="▣", layout="wide")

st.markdown(
    """
    <style>
    :root { --ink:#17212b; --muted:#61717c; --teal:#0b6e69; --mint:#e8f4f1; --gold:#e6c36a; }
    .stApp { background: #f7f8f5; color: var(--ink); }
    .block-container { max-width: 1180px; padding-top: 2.2rem; }
    h1,h2,h3 { color: var(--ink); letter-spacing: 0; }
    .hero { background: #123f43; color: #f6faf7; padding: 28px 32px; border-radius: 14px; margin-bottom: 18px; }
    .hero h1 { color: #f6faf7; margin: 0 0 8px; font-size: 2.25rem; }
    .hero p { margin: 0; color: #d8e9e5; max-width: 720px; }
    .tool-log { border: 1px solid #b9d8d1; background: var(--mint); padding: 10px 14px; margin: 8px 0; border-radius: 8px; font-size: .93rem; }
    .guide-title { font-size: 1.15rem; font-weight: 700; color: var(--teal); }
    .muted { color: var(--muted); }
    .stButton>button { border-radius: 8px; }
    </style>
    <div class='hero'><h1>校园办事指南助手</h1><p>把一句模糊的校园事务问题，转成可执行的办理步骤、材料清单和可下载文件。所有工具调用都会显示在右侧。</p></div>
    """,
    unsafe_allow_html=True,
)


def local_plan(user_text: str) -> tuple[list[ToolCall], str]:
    """Deterministic demo planner: emits ToolCall objects, then dispatches them.

    In classroom mode this keeps the demo runnable without a key. With an
    OpenAI-compatible key, `model_run` can replace this planner.
    """
    text = user_text.strip()
    guides = search_guides(text)
    if not guides:
        return [ToolCall("search_guides", {"query": text})], "我暂时没有匹配到指南，请换一个事务关键词。"
    selected = guides[0]
    calls = [
        ToolCall("search_guides", {"query": text}),
        ToolCall("get_requirements", {"guide_id": selected["id"]}),
    ]
    if any(word in text for word in ["清单", "材料", "需要", "准备", "怎么办", "步骤", "流程"]):
        calls.append(ToolCall("build_checklist", {"guide_id": selected["id"], "student_context": text}))
    return calls, selected["id"]


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
    mode = st.radio("规划模式", ["本地演示模式", "OpenAI 兼容模型（可选）"], help="没有 API Key 时会自动使用本地演示模式。")
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
            model_result = model_run(prompt) if mode.startswith("OpenAI") else None
            if model_result:
                calls, results = model_result
            else:
                calls, _ = local_plan(prompt)
                results = []
                for call in calls:
                    try:
                        results.append(execute_tool(call))
                    except Exception as error:
                        results.append({"error": str(error)})
            st.session_state.history.append({"prompt": prompt, "calls": calls, "results": results})
            render_result(calls, results)
    elif st.session_state.history:
        latest = st.session_state.history[-1]
        render_result(latest["calls"], latest["results"])

with right:
    st.subheader("工具调用过程")
    if st.session_state.history:
        for entry in st.session_state.history[-1]["calls"]:
            st.markdown(f"<div class='tool-log'><b>调用工具：</b>{entry.name}<br><span class='muted'>参数：{entry.arguments}</span></div>", unsafe_allow_html=True)
    else:
        st.info("提交问题后，这里会显示 search_guides → get_requirements → build_checklist 的执行链。")
    st.markdown("### 当前工具数量")
    st.metric("可调用业务操作", "4")
