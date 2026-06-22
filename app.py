"""
🚀 周报一键生成器 · AI Weekly Report Generator
输入几个关键词 → AI 生成专业周报 → 一键复制发出去

支持模型: DeepSeek / Qwen / OpenAI 兼容
Run: streamlit run app.py
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI 周报生成器",
    page_icon="📝",
    layout="centered",
)

st.markdown("""
<style>
    .report-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        padding: 24px;
        margin: 12px 0;
        border: 1px solid #cbd5e1;
        white-space: pre-wrap;
        line-height: 1.8;
    }
    .big-emoji { font-size: 3rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ═══════════════ 模型配置 ═══════════════
MODELS = {
    "DeepSeek (省钱·推荐)": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-v4-flash",
    },
    "Qwen-Plus": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    "Qwen-Max": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-max",
    },
}

# ═══════════════ 侧边栏 ═══════════════
with st.sidebar:
    st.title("📝 AI 周报生成器")
    st.caption("输入关键词 → AI 写周报 → 复制发送")

    model_choice = st.selectbox("🤖 模型", list(MODELS.keys()), index=0)
    cfg = MODELS[model_choice]

    api_key = st.text_input(
        "🔑 API Key",
        type="password",
        value=os.getenv("DEEPSEEK_API_KEY", ""),
        placeholder="sk-...",
    )
    if not api_key:
        st.info("已从 .env 自动加载 Key ✅" if os.getenv("DEEPSEEK_API_KEY") else "去 platform.deepseek.com 免费获取")

    st.divider()
    st.caption("💡 提示：生成的周报仅供参考，请根据实际情况修改")

# ═══════════════ 主界面 ═══════════════
st.title("📝 周报一键生成器")
st.caption("输入这周干的几件事，AI 帮你写成漂亮周报，30 秒搞定")

# ── 输入区 ──
st.subheader("✏️ 输入这周做的事")
st.caption("随便写，口语化就行，不用管格式")

col1, col2 = st.columns(2)
with col1:
    role = st.text_input("👤 你的岗位", placeholder="产品经理 / 程序员 / 运营 / 销售...")
with col2:
    style = st.selectbox("🎨 风格", ["专业正式", "简洁高效", "成果导向", "互联网轻松风"])

what_did = st.text_area(
    "📋 这周做了什么",
    placeholder="比如：\n- 对接了3个客户需求\n- 修了登录页的bug\n- 跟设计开了评审会\n- 写了下季度规划文档",
    height=150,
)

next_week = st.text_input(
    "🔜 下周计划（可选）",
    placeholder="继续推进XX项目、跟进XX客户...",
)

col_a, col_b = st.columns(2)
with col_a:
    extra = st.text_input("💡 额外想提的亮点/感想（可选）", placeholder="学到了XX、解决了XX难题...")
with col_b:
    length = st.select_slider("📏 报告长度", ["简短", "标准", "详细"], value="标准")

generate = st.button("🚀 一键生成周报", type="primary", use_container_width=True)

# ── 生成逻辑 ──
if generate:
    if not role or not what_did:
        st.warning("至少填一下岗位和这周做的事～")
    else:
        # 先检查 API Key
        key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not key:
            st.error("请填写 API Key！去 platform.deepseek.com 免费注册获取")
        else:
            prompt = f"""请根据以下信息，生成一份{style}风格的{role}工作周报。

本周工作内容：
{what_did}

下周计划：{next_week if next_week else '无'}
额外亮点：{extra if extra else '无'}
长度要求：{length}

要求：
- 分类整理，逻辑清晰（不要简单罗列）
- 突出成果和影响，用数据说话
- 语言{style}
- 包含"本周完成""下周计划""心得思考"三个板块
- 不要编造信息，只基于提供的内容展开
- {length == '简短' and '控制在200字以内' or length == '详细' and '展开详细描述，500-800字' or '300-500字'}"""

            with st.spinner("✍️ AI 正在帮你写周报..."):
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=key, base_url=cfg["base_url"])
                    resp = client.chat.completions.create(
                        model=cfg["model"],
                        messages=[
                            {"role": "system", "content": "你是一个专业的职场周报撰写助手，擅长帮人把零散的工作内容整理成结构清晰、亮点突出的周报。"},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.7,
                        max_tokens=2048,
                    )
                    result = resp.choices[0].message.content

                    st.success("✅ 周报生成完毕！")
                    st.divider()
                    st.subheader("📋 你的周报")
                    st.markdown(f'<div class="report-card">{result}</div>', unsafe_allow_html=True)

                    # 下载和复制
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.download_button(
                            "📥 下载周报 (.txt)",
                            data=result,
                            file_name=f"周报_{datetime.now().strftime('%m%d')}.txt",
                            mime="text/plain",
                            use_container_width=True,
                        )
                    with col_d2:
                        st.button("📋 一键复制（上方选中文字→Cmd+C）", use_container_width=True)

                    st.info(f"💡 对结果不满意？修改输入区的内容或切换风格，再点一次生成。")

                except Exception as e:
                    st.error(f"生成失败: {e}")
                    st.caption("检查 API Key 是否正确，或切换模型试试")

# ═══════════════ 底部 ═══════════════
st.divider()
st.caption("📝 AI 周报生成器 · 基于 DeepSeek · 数据不上传服务器 · 仅供效率辅助")
