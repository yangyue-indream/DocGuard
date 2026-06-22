"""
╔══════════════════════════════════════════════════════════════╗
║  🛡️ DocGuard — AI Autopilot for Document Review            ║
║  Qwen Global AI Hackathon 2026 · Track 4: Autopilot Agent  ║
║  Built with ❤️ by 小可                                      ║
║                                                            ║
║  Architecture:                                              ║
║  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐ ║
║  │ PDF/TXT  │──▶│ Autopilot│──▶│ Human-in │──▶│ Report  │ ║
║  │ Upload   │   │ AI Review│   │ the-Loop│   │ Export  │ ║
║  └──────────┘   └──────────┘   └──────────┘   └─────────┘ ║
║                      ▲                          ▲           ║
║                 Qwen / DeepSeek            Approve/Reject   ║
╚══════════════════════════════════════════════════════════════╝

Run: streamlit run app.py
"""

import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ═══════════════ 页面配置 ═══════════════
st.set_page_config(
    page_title="DocGuard · Autopilot Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════ 自定义样式 ═══════════════
st.markdown("""
<style>
    .risk-high {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .risk-medium {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .risk-low {
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 14px 18px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .workflow-step {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 4px 0;
    }
    .workflow-step-done {
        background: linear-gradient(135deg, #065f46 0%, #10b981 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .stat-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
    }
    .clause-item {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px;
        margin: 10px 0;
        transition: all 0.2s;
    }
    .clause-item:hover {border-color: #2563eb; box-shadow: 0 2px 8px rgba(37,99,235,0.1);}
</style>
""", unsafe_allow_html=True)

# ═══════════════ 模型配置 ═══════════════
MODEL_CONFIGS = {
    "Qwen-Plus (推荐)": {
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "description": "阿里云通义千问 · 比赛官方推荐 · 免费额度",
    },
    "Qwen-Max (最强)": {
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-max",
        "description": "最强推理能力 · 适合复杂合同",
    },
    "Qwen-Turbo (极速)": {
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-turbo",
        "description": "超快响应 · 适合快速扫描",
    },
    "DeepSeek-V4-Flash (省钱)": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-v4-flash",
        "description": "极致性价比 · ¥0.14/百万token · 注册送500万",
    },
}

# ═══════════════ 审查 Prompt（Track4 Autopilot 专用） ═══════════════
AUTOPILOT_SYSTEM_PROMPT = """你是一个企业级 AI Autopilot Agent，专门负责自动化文档审查工作流。
你的任务：自动扫描合同/文档，识别条款类型、评估风险、生成修改建议。

## 输出格式（严格 JSON）

请输出以下 JSON 结构：

{
  "document_type": "合同类型",
  "overall_risk": "high/medium/low",
  "summary": "一句话总结",
  "clauses": [
    {
      "id": 1,
      "category": "违约金/保密/终止/知识产权/付款/交付/免责/其他",
      "original_text": "原文引用...",
      "risk_level": "high/medium/low",
      "risk_reason": "为什么这是风险",
      "consequence": "可能的后果",
      "suggestion": "具体的修改建议",
      "revised_text": "修改后的建议文本"
    }
  ],
  "missing_clauses": ["建议补充的缺失条款"],
  "compliance_notes": "合规性备注"
}

只输出 JSON，不要其他文字。"""

QUICK_SCAN_PROMPT = """快速扫描文档风险，只标记高风险项。输出 JSON：

{
  "overall_risk": "high/medium/low",
  "high_risk_items": [
    {"text": "原文", "reason": "为什么危险", "fix": "怎么改"}
  ]
}
只输出 JSON。"""

# ═══════════════ 初始化 Session 状态 ═══════════════
DEFAULTS = {
    "workflow_stage": "upload",  # upload | autopilot | review | done
    "clauses": [],
    "review_decisions": {},
    "doc_text": "",
    "doc_name": "",
    "report_text": "",
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ═══════════════ 辅助函数 ═══════════════
def call_llm(system_prompt: str, user_prompt: str, api_key: str, config: dict) -> str:
    """调用 LLM（OpenAI 兼容 SDK，支持 Qwen/DeepSeek）"""
    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=config["base_url"],
    )
    response = client.chat.completions.create(
        model=config["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
        extra_body={"thinking": {"type": "disabled"}},  # Qwen 特定参数，不报错
    )
    return response.choices[0].message.content


def extract_text_from_file(file) -> str:
    """提取文件文本"""
    if file.name.endswith(".pdf"):
        from PyPDF2 import PdfReader
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        return file.read().decode("utf-8")


def parse_ai_response(text: str) -> dict:
    """解析 AI 返回的 JSON（可能被包裹在 markdown 代码块中）"""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


def reset_workflow():
    """重置工作流"""
    for key in DEFAULTS:
        st.session_state[key] = DEFAULTS[key]


# ═══════════════ 侧边栏 ═══════════════
with st.sidebar:
    st.title("🛡️ DocGuard")
    st.caption("AI Autopilot Agent · Track 4")
    st.caption("Qwen Global AI Hackathon 2026")

    st.divider()

    # 模型选择
    st.subheader("🤖 模型引擎")
    model_choice = st.selectbox(
        "选择模型",
        list(MODEL_CONFIGS.keys()),
        index=0,
    )
    model_config = MODEL_CONFIGS[model_choice]
    st.caption(model_config["description"])

    st.divider()

    # API Key
    if "Qwen" in model_choice:
        api_key_label = "🔑 Qwen API Key"
        api_key_help = "去阿里云 dashscope 获取"
        api_key_placeholder = "sk-..."
    else:
        api_key_label = "🔑 DeepSeek API Key"
        api_key_help = "去 platform.deepseek.com 获取（注册送500万token）"
        api_key_placeholder = "sk-..."

    api_key = st.text_input(
        api_key_label,
        type="password",
        value=os.getenv(f"{model_choice.split('-')[0].upper()}_API_KEY", ""),
        placeholder=api_key_placeholder,
        help=api_key_help,
    )

    if not api_key:
        st.warning("👆 填上 API Key！")

    st.divider()

    # 审查强度
    st.subheader("⚙️ 审查强度")
    strictness = st.select_slider(
        "严格程度",
        options=["宽松", "标准", "严格"],
        value="标准",
    )

    st.divider()

    # 工作流进度
    st.subheader("📋 工作流")
    stage = st.session_state.workflow_stage
    st.markdown(
        f'<div class="{"workflow-step-done" if stage in ("autopilot","review","done") else "workflow-step"}">'
        f'{"✅" if stage in ("autopilot","review","done") else "①"} 上传文档'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="{"workflow-step-done" if stage in ("review","done") else "workflow-step"}">'
        f'{"✅" if stage in ("review","done") else "②"} AI Autopilot 审查'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="{"workflow-step-done" if stage == "done" else "workflow-step"}">'
        f'{"✅" if stage == "done" else "③"} 人工复核 (Human-in-the-Loop)'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="{"workflow-step-done" if stage == "done" else "workflow-step"}">'
        f'{"✅" if stage == "done" else "④"} 导出报告'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("Made with ❤️ by 小可 · MIT License")

# ═══════════════ 主界面 ═══════════════
st.title("🛡️ DocGuard — AI Autopilot Agent")
st.caption(
    "企业级文档审查工作流 · AI 自动审查 → 人工复核 → 一键报告 "
    "· Qwen Global AI Hackathon Track 4"
)

# ═══════════════════════════════════════
# STAGE 1: Upload
# ═══════════════════════════════════════
if st.session_state.workflow_stage == "upload":
    st.divider()
    st.subheader("📤 Step 1: 上传文档")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "拖拽 PDF 或文本文件到此处",
            type=["pdf", "txt", "md"],
            help="上传合同、论文或任何需要审查的文档",
        )

    with col2:
        st.info("""
        **💡 试试这些：**
        - 📄 房屋租赁合同
        - 💼 劳动合同
        - 📝 服务协议
        - 🤝 保密协议 (NDA)
        - 📋 毕业论文
        """)

    if uploaded_file:
        with st.spinner("📖 读取文档中..."):
            doc_text = extract_text_from_file(uploaded_file)

        if not doc_text.strip():
            st.error("文档为空或无法读取～")
        else:
            st.session_state.doc_text = doc_text
            st.session_state.doc_name = uploaded_file.name
            st.success(f"✅ 文档加载成功 · {len(doc_text):,} 字符")

            with st.expander("📋 文档预览（前 600 字）", expanded=False):
                st.text(doc_text[:600])

            # 快速扫描 or 完整审查
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔍 完整 Autopilot 审查", type="primary", use_container_width=True):
                    st.session_state.workflow_stage = "autopilot"
                    st.session_state.quick_scan = False
                    st.rerun()
            with col_b:
                if st.button("⚡ 快速风险扫描", use_container_width=True):
                    st.session_state.workflow_stage = "autopilot"
                    st.session_state.quick_scan = True
                    st.rerun()

    # 重置按钮
    if st.button("🗑️ 清空重来"):
        reset_workflow()
        st.rerun()

# ═══════════════════════════════════════
# STAGE 2: AI Autopilot 自动审查
# ═══════════════════════════════════════
elif st.session_state.workflow_stage == "autopilot":
    st.divider()
    st.subheader("🤖 Step 2: AI Autopilot 自动审查中...")

    if not api_key:
        st.error(f"请先填写 {api_key_label}！")
        if st.button("🔙 返回上一步"):
            st.session_state.workflow_stage = "upload"
            st.rerun()
    else:
        doc_text = st.session_state.doc_text
        quick_scan = st.session_state.get("quick_scan", False)

        # 显示审查中
        with st.status(
            f"🔄 AI Autopilot 正在{'快速扫描' if quick_scan else '逐条审查'}..."
            f"（模型：{model_choice}，强度：{strictness}）",
            expanded=True,
        ) as status:
            st.write("📖 分析文档结构...")
            st.write("🔍 识别条款类型...")
            st.write("⚠️ 评估风险等级...")
            st.write("📝 生成修改建议...")

            try:
                max_len = 6000 if quick_scan else 10000
                context = doc_text[:max_len]
                if len(doc_text) > max_len:
                    context += f"\n\n(文档较长，仅分析前{max_len}字)"

                system_prompt = QUICK_SCAN_PROMPT if quick_scan else AUTOPILOT_SYSTEM_PROMPT
                raw = call_llm(
                    system_prompt=system_prompt,
                    user_prompt=f"审查以下文档（严格程度：{strictness}）：\n\n{context}",
                    api_key=api_key,
                    config=model_config,
                )

                # 解析 JSON
                data = parse_ai_response(raw)

                if quick_scan:
                    # 快速扫描转为简化 clause 列表
                    clauses = []
                    for i, item in enumerate(data.get("high_risk_items", [])):
                        clauses.append({
                            "id": i + 1,
                            "category": "高风险项",
                            "original_text": item.get("text", ""),
                            "risk_level": "high",
                            "risk_reason": item.get("reason", ""),
                            "consequence": "",
                            "suggestion": item.get("fix", ""),
                            "revised_text": "",
                        })
                    data["clauses"] = clauses
                    data["document_type"] = "快速扫描"
                    data["summary"] = f"快速扫描完成，发现 {len(clauses)} 个高风险项"

                st.session_state.clauses = data.get("clauses", [])
                st.session_state.review_data = data
                st.session_state.review_decisions = {}

                status.update(
                    label=f"✅ 审查完成！发现 {len(st.session_state.clauses)} 个条款",
                    state="complete",
                )

                # 统计
                high = sum(1 for c in st.session_state.clauses if c["risk_level"] == "high")
                med = sum(1 for c in st.session_state.clauses if c["risk_level"] == "medium")
                low = sum(1 for c in st.session_state.clauses if c["risk_level"] == "low")

                col_h, col_m, col_l = st.columns(3)
                with col_h:
                    st.metric("🔴 高风险", high)
                with col_m:
                    st.metric("🟡 中风险", med)
                with col_l:
                    st.metric("🟢 低风险", low)

                st.success("AI Autopilot 审查完成！现在进入人工复核阶段 👇")
                if st.button("▶️ 进入人工复核", type="primary"):
                    st.session_state.workflow_stage = "review"
                    st.rerun()

            except json.JSONDecodeError:
                st.error(f"AI 返回格式异常，正在重试...\n\n原始返回：\n{raw[:500]}")
                if st.button("🔄 重试审查"):
                    st.rerun()
            except Exception as e:
                st.error(f"审查出错: {e}")
                if st.button("🔙 返回重试"):
                    st.session_state.workflow_stage = "upload"
                    st.rerun()

# ═══════════════════════════════════════
# STAGE 3: Human-in-the-Loop 人工复核
# ═══════════════════════════════════════
elif st.session_state.workflow_stage == "review":
    st.divider()
    st.subheader("👤 Step 3: 人工复核 — Human-in-the-Loop")

    # 统计
    clauses = st.session_state.clauses
    decisions = st.session_state.review_decisions
    total = len(clauses)
    reviewed = len(decisions)
    approved = sum(1 for v in decisions.values() if v == "approve")
    rejected = sum(1 for v in decisions.values() if v == "reject")
    modified = sum(1 for v in decisions.values() if v == "modify")

    # 进度
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.metric("📋 总条款", total)
    with col_p2:
        st.metric("✅ 已复核", f"{reviewed}/{total}")
    with col_p3:
        if total > 0:
            pct = int(reviewed / total * 100)
            st.progress(pct / 100, text=f"进度 {pct}%")
        else:
            st.info("暂无条款")

    st.divider()

    if not clauses:
        st.info("没有需要复核的条款～")
        if st.button("▶️ 跳过，生成报告"):
            st.session_state.workflow_stage = "done"
            st.rerun()
    else:
        # 逐条显示
        for clause in clauses:
            cid = clause["id"]
            rl = clause["risk_level"]

            risk_border = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}
            risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}

            with st.container():
                st.markdown(
                    f'<div class="clause-item" style="border-left: 4px solid {risk_border.get(rl, "#6b7280")}">'
                    f'<strong>{risk_emoji.get(rl, "⚪")} #{cid} · {clause.get("category", "条款")}</strong>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                col_clause, col_action = st.columns([3, 1])

                with col_clause:
                    st.markdown(f"**📌 原文：** {clause.get('original_text', '')[:200]}")
                    st.markdown(f"**⚠️ 风险：** {clause.get('risk_reason', '')}")
                    if clause.get("suggestion"):
                        st.markdown(f"**💡 建议：** {clause.get('suggestion', '')}")
                    if clause.get("revised_text"):
                        with st.expander("📝 修改后文本"):
                            st.info(clause["revised_text"])

                with col_action:
                    current = decisions.get(cid, None)
                    st.radio(
                        f"决定 #{cid}",
                        ["待定", "✅ 采纳", "❌ 驳回", "✏️ 修改"],
                        index=0 if current is None else ["待定", "approve", "reject", "modify"].index(current) if current in ["approve", "reject", "modify"] else 0,
                        key=f"decision_{cid}",
                        horizontal=False,
                    )
                    # 存储决定
                    selected = st.session_state.get(f"decision_{cid}", "待定")
                    decision_map = {"✅ 采纳": "approve", "❌ 驳回": "reject", "✏️ 修改": "modify"}
                    if selected in decision_map:
                        st.session_state.review_decisions[cid] = decision_map[selected]

                st.divider()

        # 操作按钮
        st.divider()
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button("🔄 返回重新审查", use_container_width=True):
                st.session_state.workflow_stage = "autopilot"
                st.rerun()

        with col_btn2:
            # 一键全部采纳
            if st.button("✅ 全部采纳", use_container_width=True):
                for c in clauses:
                    st.session_state.review_decisions[c["id"]] = "approve"
                st.rerun()

        with col_btn3:
            if st.button("📊 生成最终报告 ▶️", type="primary", use_container_width=True):
                st.session_state.workflow_stage = "done"
                st.rerun()

# ═══════════════════════════════════════
# STAGE 4: 报告导出
# ═══════════════════════════════════════
elif st.session_state.workflow_stage == "done":
    st.divider()
    st.subheader("📊 Step 4: 最终审查报告")

    clauses = st.session_state.clauses
    decisions = st.session_state.review_decisions
    data = st.session_state.get("review_data", {})
    doc_name = st.session_state.doc_name

    # 统计
    total = len(clauses)
    approved = sum(1 for v in decisions.values() if v == "approve")
    rejected = sum(1 for v in decisions.values() if v == "reject")
    modified = sum(1 for v in decisions.values() if v == "modify")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 总条款", total)
    with col2:
        st.metric("✅ AI采纳", approved)
    with col3:
        st.metric("❌ 人工驳回", rejected)
    with col4:
        st.metric("✏️ 已修改", modified)

    st.divider()

    # 生成报告
    st.subheader("📝 审查报告")

    report_lines = [
        f"# 🛡️ DocGuard 审查报告",
        f"",
        f"**文档**：{doc_name}",
        f"**审查时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**审查模式**：AI Autopilot Agent + 人工复核 (Human-in-the-Loop)",
        f"**模型**：{model_choice}",
        f"**整体风险**：{data.get('overall_risk', 'N/A')}",
        f"",
        f"---",
        f"",
        f"## 📊 统计",
        f"",
        f"| 类型 | 数量 |",
        f"|------|------|",
        f"| 总条款 | {total} |",
        f"| ✅ AI建议被采纳 | {approved} |",
        f"| ❌ AI建议被驳回 | {rejected} |",
        f"| ✏️ 人工修改 | {modified} |",
        f"",
        f"---",
        f"",
        f"## 🔍 条款明细",
        f"",
    ]

    for clause in clauses:
        cid = clause["id"]
        dec = decisions.get(cid, "pending")
        dec_label = {"approve": "✅ 采纳", "reject": "❌ 驳回", "modify": "✏️ 修改"}.get(dec, "⏳ 未处理")

        report_lines.extend([
            f"### #{cid} · {clause.get('category', '条款')} · {dec_label}",
            f"",
            f"- **风险等级**：{clause.get('risk_level', 'N/A')}",
            f"- **原文**：{clause.get('original_text', '')}",
            f"- **风险说明**：{clause.get('risk_reason', '')}",
            f"- **修改建议**：{clause.get('suggestion', '')}",
        ])
        if clause.get("revised_text"):
            report_lines.append(f"- **建议文本**：{clause['revised_text']}")
        report_lines.append("")

    if data.get("missing_clauses"):
        report_lines.extend([
            "---",
            "",
            "## ⚠️ 建议补充的缺失条款",
            "",
        ])
        for mc in data["missing_clauses"]:
            report_lines.append(f"- {mc}")

    if data.get("compliance_notes"):
        report_lines.extend([
            "",
            "---",
            "",
            "## 📋 合规性备注",
            "",
            data["compliance_notes"],
        ])

    report_lines.extend([
        "",
        "---",
        "",
        "*本报告由 DocGuard AI Autopilot Agent 生成，仅供参考，不构成法律意见。*",
    ])

    report_text = "\n".join(report_lines)
    st.session_state.report_text = report_text

    # 渲染报告
    with st.expander("📄 完整报告预览", expanded=True):
        st.markdown(report_text)

    # 导出
    st.divider()
    st.subheader("📥 导出")

    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        st.download_button(
            "📝 下载 Markdown 报告",
            data=report_text,
            file_name=f"DocGuard_报告_{doc_name}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col_e2:
        # JSON 导出
        json_data = json.dumps({
            "doc_name": doc_name,
            "review_time": datetime.now().isoformat(),
            "model": model_choice,
            "data": data,
            "decisions": {str(k): v for k, v in decisions.items()},
        }, ensure_ascii=False, indent=2)
        st.download_button(
            "📦 下载 JSON 数据",
            data=json_data,
            file_name=f"DocGuard_数据_{doc_name}.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_e3:
        if st.button("🔄 重新开始", use_container_width=True):
            reset_workflow()
            st.rerun()

# ═══════════════ 页脚 ═══════════════
st.divider()
st.caption(
    "🛡️ DocGuard · AI Autopilot Agent · Track 4 · Qwen Global AI Hackathon 2026 · "
    "Made with ❤️ by 小可 · MIT License"
)
