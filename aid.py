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
    st.session_state.nature = "可爱的猫咪"
if "current_name"   not in st.session_state:
    st.session_state.current_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

sys_prompt = ("你是一个%s的%s，请按照你的性格回答问题，不能做出与你性格相反的回答。并且"
              "不能ooc")
#连接到deepseek
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")
# 初始化时主动生成欢迎语
# response = client.chat.completions.create(
#         model="deepseek-chat",
#         messages=[
#             {"role": "user", "content": "你好！"}
#
#         ],
#         stream=True
#     )
#展示聊天信息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])
# prompt=st.chat_input("尽情的享受吧！")
prompt=st.chat_input("尽情的享受吧！")
#侧边栏
with st.sidebar:
    st.header("ai会话面板")
    if st.button("新建一个会话",width="stretch",icon="👆️"):
            #保存当前会话
        save_session_state()
        if st.session_state.messages:
                st.session_state.messages=[]
                st.session_state.current_name=datetime.strftime(datetime.now(),"%Y-%m-%d %H-%M-%S")
                save_session_state()
                st.rerun()


    nick_name = st.text_input("昵称", placeholder="请输入昵称",value="(默认)布偶猫")
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_input("性格", placeholder="请输入性格",value="(默认)可爱的猫咪")
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