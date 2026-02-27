import streamlit as st
from groq import Groq
import random
import time

# 1. [요구사항] 페이지 설정: 명칭 '번개 챗봇 AI', 메뉴 상시 열림(expanded)
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# 2. [요구사항] 프리미엄 화이트 그라데이션 UI 디자인 (CSS)
# 배경은 화이트 그라데이션, 메뉴도 화이트로 복구, 버튼은 화려한 포인트 블루
st.markdown("""
    <style>
    /* 전체 배경: 은은하고 화사한 화이트-파스텔 블루 그라데이션 강제 고정 */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 100%) !important;
        background-attachment: fixed !important;
        color: #1a202c !important;
    }
    
    /* [핵심 요구사항] PC 상단 잘림 방지: 13rem 패딩 확보 */
    .block-container {
        max-width: 850px;
        padding-top: 13rem !important; 
        padding-bottom: 7rem;
    }

    /* 채팅 말풍선: 깨끗한 화이트 카드 디자인 */
    .stChatMessage {
        background-color: #ffffff !important;
        border-radius: 25px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 25px !important;
    }

    /* [긴급 수정] 사이드바(메뉴): 검정색을 지우고 다시 화이트로 고정 */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        background-image: none !important;
        border-right: 1px solid #edf2f7 !important;
    }
    [data-testid="stSidebar"] * {
        color: #2d3748 !important; /* 글자색도 어두운색으로 복구 */
    }

    /* 버튼 스타일: 시원한 블루 그라데이션 및 입체 효과 */
    .stButton>button {
        width: 100% !important;
        height: 5rem !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 1.4rem !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(58, 123, 213, 0.3) !important;
        transition: transform 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(58, 123, 213, 0.4) !important;
    }

    /* [요구사항] 가변형 사용자 이름 레이블 */
    .dynamic-user-tag {
        font-size: 1.2rem;
        color: #1e3c72;
        font-weight: 900;
        margin-bottom: 15px;
        display: block;
        border-left: 8px solid #00d2ff;
        padding-left: 15px;
    }

    /* 메인 타이틀: 세련된 텍스트 그라데이션 */
    .main-header-text {
        font-size: 3.2rem;
        font-weight: 950;
        text-align: center;
        background: linear-gradient(to right, #1e3c72, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 3.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 보안 설정
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 API 키 설정 확인 필요!")
    st.stop()

# 4. 세션 상태 (사용자 이름 가변 반영)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자"

# 5. [요구사항] 한자/중국어 박멸 페르소나 설정
HANJA_KILL_RULE = "한자(漢字)나 중국어를 절대 쓰지 마세요. 무조건 한국어 단어만 사용하세요."

persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 코딩 선생님이야. {st.session_state.user_name}님에게 한국어로만 알려줘. {HANJA_KILL_RULE}",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 비서야. 한국어로만 도와줘. {HANJA_KILL_RULE}",
    "🎭 실시간 역할 변신": f"너는 역할극 전문가야. {st.session_state.user_name}님이 정해준 인물로 한국어 대화해. {HANJA_KILL_RULE}",
    "🎲 운빨 테스트": f"너는 예언가야. {st.session_state.user_name}님의 운세를 유쾌한 한국어로만 리액션해줘. {HANJA_KILL_RULE}"
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. 사이드바 메뉴 (하얀색 바탕에 번개 챗봇 AI 명칭 고정)
with st.sidebar:
    st.markdown("<h1 style='color:#1e3c72; font-size: 1.8rem;'>⚡ 번개 챗봇 AI</h1>", unsafe_allow_html=True)
    st.session_state.user_name = st.text_input("👤 당신의 이름", value=st.session_state.user_name)
    st.divider()
    
    selected = st.radio("기능 선택", list(persona_base.keys()), index=list(persona_base.keys()).index(st.session_state.current_mode))
    
    if selected != st.session_state.current_mode:
        st.session_state.current_mode = selected
        st.rerun()
    
    st.divider()
    # [요구사항] 기능별 기록 삭제 버튼
    if st.button(f"🗑️ {selected} 기록 삭제"):
        st.session_state.multi_chat_history[selected] = []
        st.rerun()

# 7. 화면 렌더링
messages = st.session_state.multi_chat_history[selected]
system_msg = {"role": "system", "content": persona_base[selected]}
if not messages or messages[0]["role"] != "system":
    messages.insert(0, system_msg)
else:
    messages[0] = system_msg

st.markdown(f'<div class="main-header-text">⚡ {selected}</div>', unsafe_allow_html=True)

for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. 입력창 및 가변 이름 레이블
st.markdown(f'<span class="dynamic-user-tag">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("메시지를 입력해 주세요! ⚡"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 한자 차단을 위해 temperature 0.0 고정
        placeholder = st.empty(); full_ans = ""
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0,
            stream=True
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                full_ans += content
                placeholder.markdown(full_ans + "▌")
        placeholder.markdown(full_ans)
        messages.append({"role": "assistant", "content": full_ans})