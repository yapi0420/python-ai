import streamlit as st
import os
from openai import OpenAI
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

#左侧侧边栏
with st.sidebar:
    st.header("操作栏")
    nick_name = st.text_input("昵称", placeholder="请输入昵称",value="(默认)布偶猫")
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_input("性格", placeholder="请输入性格",value="(默认)可爱的猫咪")
    if nature:
        st.session_state.nature = nature

#展示聊天信息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])
prompt=st.chat_input("尽情的享受吧！")
if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role":"user","content":prompt})
else :
    prompt="喵喵喵"
sys_prompt = ("你是一个%s的%s，请按照你的性格回答问题，不能做出与你性格相反的回答。并且"
              "不能ooc")
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": sys_prompt % (st.session_state.nick_name, st.session_state.nature)},
        #滚雪球方法，把之前的消息都放进去
        *st.session_state.messages
    ],
    stream=True
)
#非流式输出
# st.chat_message("assistant").write(response.choices[0].message.content)
# st.session_state.messages.append({"role":"assistant","content":response.choices[0].message.content})
#流式输出
liushi=st.empty()
allliushi=""
for chuck in response:
    content =chuck.choices[0].delta.content
    allliushi=allliushi+content
    liushi.chat_message(allliushi).write(allliushi)
st.session_state.messages.append({"role":"assistant","content":allliushi})