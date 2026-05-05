import ollama
import streamlit as st


# ====================== 初始化（必写）======================
def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "kb_text" not in st.session_state:
        st.session_state.kb_text = ""


init_session_state()


# ====================== 流式聊天函数 ======================
def stream_ollama(model_name, prompt):
    messages = [
        {"role": "system", "content": "你是一个专业、严谨、有用的AI助手。请根据提供的知识库回答问题。"},
        {"role": "user", "content": prompt}
    ]

    for chunk in ollama.chat(
            model=model_name,
            messages=messages,
            stream=True,
            options={"temperature": 0}
    ):
        content = chunk["message"].get("content", "")
        yield content


# ====================== 拼接知识库提示词 ======================
def build_prompt(kb_text, question):
    if not kb_text:
        return question
    return f"""
请根据下面的知识库内容回答问题。
如果知识库中没有相关信息，请直接说：“知识库中未找到相关内容”。

======== 知识库 ========
{kb_text}
========================

用户问题：{question}
"""


# ====================== 前端界面 ======================
st.set_page_config(page_title="AI知识库助手", layout="wide")
st.title("🤖 本地知识库 AI 聊天机器人")

# 侧边栏
with st.sidebar:
    st.subheader("⚙ 模型设置")
    model_name = st.selectbox("选择模型", ["qwen2:0.5b", "qwen2:1.5b"])

    st.subheader("📚 知识库")
    uploaded_file = st.file_uploader("上传 TXT 知识库", type="txt")
    if uploaded_file:
        st.session_state.kb_text = uploaded_file.read().decode("utf-8")
        st.success("✅ 知识库已加载")

    st.divider()
    if st.button("🗑 清空对话记录"):
        st.session_state.chat_history = []
        st.rerun()

# 展示历史消息
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入框
if question := st.chat_input("请输入你的问题..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.chat_history.append({"role": "user", "content": question})

    # 构造提示词
    prompt = build_prompt(st.session_state.kb_text, question)

    # AI 回答
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_ans = ""

        for chunk in stream_ollama(model_name, prompt):
            full_ans += chunk
            placeholder.markdown(full_ans + "▌")

        placeholder.markdown(full_ans)

    st.session_state.chat_history.append({"role": "assistant", "content": full_ans})
