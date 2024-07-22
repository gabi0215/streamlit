# Streamlit 등 필요한 라이브러리 임포트
import streamlit as st
import time
from langchain_core.messages import HumanMessage, AIMessage
from utils import load_model , load_prompt, set_memory, initialize_chain, generate_message

# 애플리케이션 제목 설정
st.title("페르소나 챗봇")
st.markdown("<br>", unsafe_allow_html=True)  # 브라우저에 줄 바꿈을 삽입합니다.
# load_model(model_name='gpt-4o')

# 사용자로부터 캐릭터를 선택하는 옵션
character_name = st.selectbox(
    "**캐릭터 골라줘!**", ("trump","biden"),
    index = 0, key="character_name_select"
)
# print("캐릭터 이름")
# 선택한 캐릭터를 Session 에 저장
st.session_state.character_name = character_name
# 사용자로부터 모델 버전 선택하는 옵션
model_name = st.selectbox(
    "**모델을 골라줘!**",
    ("gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo","gpt-4o-mini"),
    index=0,
    key="model_name_select",
)
# 선택한 모델 버전을 session 에 저장
st.session_state.model_name = model_name
# session 에서 채팅을 시작하겠다는 확인 및 초기화
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False
    st.session_state.memory = None
    st.session_state.chain =None

# 채팅을 시작하는 함수 정의
def start_chat() -> None:
    """선택된 모델을 기반으로 채팅을 시작하는 함수입니다.
    """
    #모델불러오기
    llm = load_model(st.session_state.model_name)
    st.session_state.chat_started = True
    st.session_state.memory = set_memory()
    st.session_state.chain = initialize_chain(
        llm = llm,
        character_name=st.session_state.character_name,
        memory=st.session_state.memory
    )
# 채팅 시작
# 만약 버튼을 누르면 시작 "분기처리"
if st.button("Start Chat"):
    start_chat()

if st.session_state.chat_started:
    if st.session_state.memory is None or st.session_state.chain is None:
        start_chat()
    
    for message in st.session_state.memory.chat_memory.messages:
        # 메세지가 user input 인지 ai output인지 확인
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message,AIMessage):
            role = "assistant"
        else:
            continue
        with st.chat_message(role):
            st.markdown(message.content)

    if prompt := st.chat_input():
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            # message를 담을 공간
            message_placehloder = st.empty()
            full_response = ""
            response = generate_message(
                st.session_state.chain,prompt
            )
            #"" -> "아버지 " -> "아버지가 방에 " -> "아버지가 방에 들어가신다 "
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placehloder.markdown(full_response+"▌ ")
            message_placehloder.markdown(full_response.strip())