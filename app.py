import streamlit as st
from groq import Groq
import random
import time

# 1. [요구사항] 페이지 설정: 명칭 '번개 챗봇 AI', 메뉴 상시 열림
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# 2. [요구사항] 초강력 프리미엄 컬러 UI 디자인 (CSS)
# 모든 색상에 !important를 붙여 디자인이 변하지 않도록 강제 잠금했습니다.
st.markdown("""
    <style>
    /* 전체 배경: 화사하고 입체적인 블루-라이트 퍼플 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%) !important;
        background-attachment: fixed !important;
        color: #1a202c !important;
    }
    
    /* [핵심 요구사항] PC 상단 잘림 방지: 13rem 패딩 확보 */
    .block-container {
        max-width: 850px;
        padding-top: 13rem !important; 
        padding-bottom: 7rem;
    }

    /* 채팅 말풍선: 깨끗한 화이트와 부드러운 그림자 */
    .stChatMessage {
        background-color: #ffffff !important;
        border-radius: 25px !important;
        border: 1px solid #d1d9e6 !important;
        box-shadow: 10px 10px 20px #babecc, -10px -10px 20px #ffffff !important;
        margin-bottom: 25px !important;
        padding: 1.5rem !important;
    }

    /* [긴급 수정] 사이드바(메뉴): 깨끗한 화이트 그라데이션으로 고정 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f7faff 100%) !important;
        border-right: 2px solid #e2e8f0 !important;
    }
    [data-testid="stSidebar"] * {
        color: #2d3748 !important;
    }

    /* [요구사항] 버튼 스타일: 시선을 사로잡는 네온 블루 그라데이션 */
    .stButton>button {
        width: 100% !important;
        height: 5.5rem !important;
        border-radius: 25px !important;
        background: linear-gradient(135deg, #6dd5ed 0%, #2193b0 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 1.5rem !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(33, 147, 176, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 15px 30px rgba(33, 147, 176, 0.5) !important;
        filter: brightness(1.1);
    }

    /* [요구사항] 가변형 사용자 이름 레이블: 선명한 블루 포인트 */
    .user-dynamic-label {
        font-size: 1.3rem;
        color: #2193b0;
        font-weight: 900;
        margin-bottom: 15px;
        display: block;
        border-left: 10px solid #6dd5ed;
        padding-left: 15px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 0 15px 15px 0;
    }

    /* 메인 타이틀: 텍스트 그라데이션 적용 */
    .main-title-gradient {
        font-size: 3.5rem;
        font-weight: 950;
        text-align: center;
        background: linear-gradient(to right, #2193b0, #6dd5ed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 3.5rem;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
    }

    /* 하단 입력창 배경 투명화 */
    .stChatInputContainer {
        background: transparent !important;
        padding-bottom: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 보안 설정
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 .streamlit/secrets.toml 파일에 API 키를 등록해주세요!")
    st.stop()

# 4. 세션 상태 (사용자 이름 가변형)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자"

# 5. [요구사항] 페르소나 및 한자 완벽 박멸 지침
STRICT_KOREAN = "한자(漢字)나 중국어를 절대 사용하지 마세요. 오직 순수 한국어(한글)로만 답변하세요."

persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 코딩 선생님이야. {st.session_state.user_name}님에게 한국어로만 친절히 가르쳐줘. {STRICT_KOREAN}",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 비서야. 모든 업무를 한국어로만 도와줘. {STRICT_KOREAN}",
    "🎭 실시간 역할 변신": f"너는 역할극 전문가야. {st.session_state.user_name}님이 정한 인물로 한국어 대화해. {STRICT_KOREAN}",
    "🎲 운빨 테스트": f"너는 예언가야. {st.session_state.user_name}님의 운세를 유쾌한 한국어로 리액션해줘. {STRICT_KOREAN}"
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. [요구사항] 사이드바 (명칭: 번개 챗봇 AI)
with st.sidebar:
    st.markdown("<h1 style='color:#2193b0; font-size: 2rem; font-weight:900;'>⚡ 번개 챗봇 AI</h1>", unsafe_allow_html=True)
    st.session_state.user_name = st.text_input("👤 당신의 이름 입력", value=st.session_state.user_name)
    st.divider()
    
    selected = st.radio("모드 선택", list(persona_base.keys()), index=list(persona_base.keys()).index(st.session_state.current_mode))
    
    if selected != st.session_state.current_mode:
        st.session_state.current_mode = selected
        st.rerun()
    
    st.divider()
    # [요구사항] 기능별 삭제 버튼
    if st.button(f"🗑️ {selected} 기록 삭제"):
        st.session_state.multi_chat_history[selected] = []
        st.rerun()
    st.caption("Premium Gradient Edition")

# 7. 메인 화면 렌더링
messages = st.session_state.multi_chat_history[selected]
system_msg = {"role": "system", "content": persona_base[selected]}
if not messages or messages[0]["role"] != "system":
    messages.insert(0, system_msg)
else:
    messages[0] = system_msg

st.markdown(f'<div class="main-title-gradient">⚡ {selected}</div>', unsafe_allow_html=True)

for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. 입력 영역 (가변 이름 레이블 적용)
st.markdown(f'<span class="user-dynamic-label">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("이곳에 질문을 입력하세요! ⚡"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 한자 방지를 위해 temperature 0.0 고정
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