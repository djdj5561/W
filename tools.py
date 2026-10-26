"""Business tools for the Campus Guide Assistant.

Each public function is intentionally small and independently testable. The
agent layer calls these functions through the TOOL_REGISTRY, making Tool
Calling visible and auditable during a classroom demonstration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any, Callable


DATA_PATH = Path(__file__).parent / "data" / "guides.json"


def load_guides() -> list[dict[str, Any]]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def search_guides(query: str, category: str = "全部") -> list[dict[str, Any]]:
    """Search the local, auditable campus guide dataset."""
    normalized_query = query.lower().replace("？", "").replace("，", " ")
    terms = [term for term in normalized_query.split() if term]
    guides = load_guides()
    if category != "全部":
        guides = [guide for guide in guides if guide["category"] == category]
    scored: list[tuple[int, dict[str, Any]]] = []
    for guide in guides:
        haystack = " ".join(
            [guide["title"], guide["category"], guide["summary"], *guide["keywords"]]
        ).lower()
        keyword_hits = sum(2 for keyword in guide["keywords"] if keyword.lower() in normalized_query)
        phrase_hits = sum(1 for term in terms if term in haystack)
        score = keyword_hits + phrase_hits
        if score or not terms:
            scored.append((score, guide))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [guide for _, guide in scored[:3]]


def get_requirements(guide_id: str) -> dict[str, Any] | None:
    """Return the steps and materials for one selected guide."""
    return next((guide for guide in load_guides() if guide["id"] == guide_id), None)


def build_checklist(guide_id: str, student_context: str = "") -> str:
    """Create an exportable Markdown checklist from a guide."""
    guide = get_requirements(guide_id)
    if not guide:
        raise ValueError("找不到对应的办事指南")
    context = student_context.strip() or "未填写"
    lines = [
        f"# {guide['title']}：办理清单",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 使用场景：{context}",
        f"> 办理部门：{guide['department']}",
        f"> 办理地点：{guide['location']}",
        "",
        "## 办理步骤",
        *[f"- [ ] {step}" for step in guide["steps"]],
        "",
        "## 所需材料",
        *[f"- [ ] {material}" for material in guide["materials"]],
        "",
        f"**提示：** {guide['official_note']}",
    ]
    return "\n".join(lines)


def submit_application(guide_id: str, student_context: str = "", confirmed: bool = False) -> dict[str, str]:
    """Simulate a submission, requiring explicit confirmation first.

    This never contacts a real school system; it demonstrates the permission
    boundary required for a state-changing operation.
    """
    if not confirmed:
        raise PermissionError("提交前必须获得用户明确确认")
    guide = get_requirements(guide_id)
    if not guide:
        raise ValueError("找不到对应的办事指南")
    reference = f"DEMO-{guide_id.upper()}-001"
    return {"reference": reference, "status": "已创建本地模拟申请", "context": student_context or "未填写"}


def markdown_to_html(markdown: str) -> str:
    """Small dependency-free renderer for the exported checklist."""
    rows = []
    in_list = False
    for raw in markdown.splitlines():
        line = escape(raw)
        if line.startswith("# "):
            rows.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            rows.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- [ ] "):
            if not in_list:
                rows.append("<ul>")
                in_list = True
            rows.append(f"<li><input type='checkbox'> {line[6:]}</li>")
        elif line.startswith("> "):
            rows.append(f"<p class='meta'>{line[2:]}</p>")
        elif line.startswith("**提示：**"):
            rows.append(f"<p class='note'>{line}</p>")
        elif line:
            if in_list:
                rows.append("</ul>")
                in_list = False
            rows.append(f"<p>{line}</p>")
    if in_list:
        rows.append("</ul>")
    return """<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>校园办事清单</title>
<style>body{font-family:system-ui,sans-serif;max-width:760px;margin:48px auto;padding:0 24px;color:#17212b;line-height:1.7}h1{font-size:2rem}h2{margin-top:32px;color:#0b6e69}.meta{color:#52616b;font-size:.95rem}.note{padding:12px 16px;background:#fff3d6;border:1px solid #e6c36a;border-radius:8px}li{margin:8px 0}</style>
<body>""" + "".join(rows) + "</body></html>"


TOOL_REGISTRY: dict[str, Callable[..., Any]] = {
    "search_guides": search_guides,
    "get_requirements": get_requirements,
    "build_checklist": build_checklist,
    "submit_application": submit_application,
}


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


def execute_tool(call: ToolCall) -> Any:
    if call.name not in TOOL_REGISTRY:
        raise ValueError(f"未知工具：{call.name}")
    return TOOL_REGISTRY[call.name](**call.arguments)
