import ollama
import streamlit as st


# 初始化
def init_session():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'kb_text' not in st.session_state:
        st.session_state.kb_text = ""


init_session()


# 流式输出
def stream_chat(model, prompt):
    messages = [
        {'role': 'system', 'content': '你是一个有用的AI助手'},
        {'role': 'user', 'content': prompt}
    ]
    for chunk in ollama.chat(model=model, messages=messages, stream=True):
        yield chunk['message']['content']


# 界面 + 聊天逻辑
st.set_page_config(page_title='AI聊天机器人', layout='wide')
st.title('🤖 本地知识库AI助手')

# 侧边栏
with st.sidebar:
    model_name = st.selectbox('选择模型', ['qwen2:0.5b'])
    uploaded_file = st.file_uploader('上传知识库TXT', type='txt')
    if uploaded_file:
        st.session_state.kb_text = uploaded_file.read().decode('utf-8')
        st.success('知识库已加载')

# 展示历史
for msg in st.session_state.chat_history:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# 输入框
if prompt := st.chat_input('输入问题'):
    # 显示用户消息
    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.chat_history.append({'role': 'user', 'content': prompt})

    # 拼接知识库
    kb = st.session_state.kb_text
    full_prompt = f'知识库:{kb}\n用户问题:{prompt}' if kb else prompt

    # AI 回答
    with st.chat_message('assistant'):
        placeholder = st.empty()
        ans = ''
        for chunk in stream_chat(model_name, full_prompt):
            ans += chunk
            placeholder.markdown(ans + '')
        placeholder.markdown(ans)
    st.session_state.chat_history.append({"role": "assistant", "content": ans})
