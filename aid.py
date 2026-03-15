import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

def save_session_state():
    if st.session_state.current_name:
        now_session = {
            "messages": st.session_state.messages,
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_name": st.session_state.current_name
        }
        if not os.path.exists("sessions"):
            os.mkdir("sessions")
        # 保存会话数据
        with open("sessions/" + st.session_state.current_name + ".json", 'w', encoding='utf-8') as f:
            json.dump(now_session, f, ensure_ascii=False, indent=2)

st.set_page_config(
    page_title="AI Friend",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

#大标题
st.title("AI Friend")
if "messages" not in st.session_state:
    st.session_state.messages =[]
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "布偶猫"
if "nature" not in st.session_state:
    st.session_state.nature = "傲娇的猫咪"
if "current_name"   not in st.session_state:
    st.session_state.current_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

sys_prompt = ("你是一个%s的%s，请按照你的性格回答问题，不能做出与你性格相反的回答。并且"
              "不能ooc")
#加载会话数据
def load_session_state():
    session_list=[]
    if os.path.exists("sessions"):
        file_list=os.listdir("sessions")
        for file in file_list:
            if file.endswith(".json"):
                session_list.append(file[:-5])
    session_list.sort(reverse=True)
    return session_list
def load_sessions_state(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            # 读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_name = session_name
    except Exception:
        st.error("加载会话失败!")
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json") # 删除文件
            # 如果删除的是当前会话, 则需要更新消息列表
            if session_name == st.session_state.current_name:
                st.session_state.messages = []
                st.session_state.current_name =datetime.strftime(datetime.now(),"%Y-%m-%d %H-%M-%S")
    except Exception:
        st.error("删除会话失败!")
#连接到deepseek
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")
#主动生成欢迎语言（基于默认昵称和性格）
# st.chat_message("assistant").write())

#展示聊天信息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])
# prompt=st.chat_input("尽情的享受吧！")
prompt=st.chat_input("尽情的享受吧！")
#侧边栏
with st.sidebar:
    # st.subheader("会话历史")
    st.header("ai会话面板")
    if st.button("新建一个会话",width="stretch",icon="👆️"):
            #保存当前会话
        save_session_state()
        if st.session_state.messages:
                st.session_state.messages=[]
                st.session_state.current_name=datetime.strftime(datetime.now(),"%Y-%m-%d %H-%M-%S")
                save_session_state()
                st.rerun()
    st.divider()
    st.text("会话历史：")
    session_list=load_session_state()
    # current_name=st.selectbox("选择会话",session_list)
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            # 加载会话信息
            # 三元运算符: 如果条件为真, 则返回第一个表达式的值; 否则, 返回第二个表达式的值 --> 语法: 值1 if 条件 else 值2
            if st.button(session, width="stretch", icon="📄", key=f"load_{session}",
                         type="primary" if session == st.session_state.current_name else "secondary"):
                load_sessions_state(session)
                st.rerun()
        with col2:
            # 删除会话信息
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()


    nick_name = st.text_input("昵称", placeholder="请输入昵称",value="(默认)布偶猫")
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_input("性格", placeholder="请输入性格",value="(默认)傲娇的猫咪")
    if nature:
        st.session_state.nature = nature


if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role":"user","content":prompt})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": sys_prompt % (st.session_state.nick_name, st.session_state.nature)},
            #滚雪球方法，把之前的消息都放进去
            *st.session_state.messages
        ],
        stream=True
    )
    liushi=st.empty()
    allliushi=""
    for chuck in response:
        content =chuck.choices[0].delta.content
        allliushi=allliushi+content
        liushi.chat_message(allliushi).write(allliushi)
    st.session_state.messages.append({"role":"assistant","content":allliushi})
    save_session_state()