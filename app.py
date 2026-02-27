import streamlit as st
from groq import Groq
import random
import time

# [요구사항 1] 페이지 설정: PC에서 메뉴(사이드바) 기본 열림 고정 및 타이틀 설정
st.set_page_config(
    page_title="번개 챗봇 AI - 상훈 에디션",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# [요구사항 2 & 3] 프리미엄 UI 디자인 & 다크모드 배제 (화이트/블루 고정)
# [요구사항 4] PC 상단 잘림 방지 (padding-top 11rem으로 극대화)
st.markdown("""
    <style>
    /* 전체 배경: 화이트톤의 깨끗한 그라데이션 */
    .stApp {
        background: #ffffff !important;
        background-image: linear-gradient(180deg, #ffffff 0%, #f2f7ff 100%) !important;
        color: #1a202c !important;
    }
    
    /* PC 상단 여백: 메뉴바에 제목이 가려지지 않도록 11rem 확보 */
    .block-container {
        max-width: 800px;
        padding-top: 11rem !important; 
        padding-bottom: 7rem;
    }

    /* 채팅 말풍선: 고급스러운 카드형 UI */
    .stChatMessage {
        background-color: #ffffff !important;
        border-radius: 22px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.06) !important;
        margin-bottom: 25px;
    }

    /* 사이드바 스타일: 화이트 고정 및 구분선 */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #f0f4f8 !important;
    }

    /* [요구사항 5] 모바일 최적화 버튼: 누르기 편하게 크기를 키우고 화려한 그라데이션 적용 */
    .stButton>button {
        width: 100% !important;
        height: 4.8rem !important;
        border-radius: 22px !important;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 1.3rem !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(58, 123, 213, 0.3) !important;
        transition: transform 0.2s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }

    /* [요구사항 6] 가변형 사용자 이름 레이블: 입력창 위에 역동적으로 배치 */
    .dynamic-user-label {
        font-size: 1.2rem;
        color: #1e3c72;
        font-weight: 900;
        margin-bottom: 18px;
        display: block;
        border-left: 8px solid #00d2ff;
        padding-left: 20px;
    }

    /* 메인 타이틀 디자인 */
    .main-title {
        font-size: 3rem;
        font-weight: 950;
        text-align: center;
        color: #1e3c72;
        margin-bottom: 3.5rem;
        letter-spacing: -2px;
    }
    </style>
    """, unsafe_allow_html=True)

# API 로드
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 API 키를 확인해주세요!")
    st.stop()

# [요구사항 6 반영] 사용자 이름 세션 상태 (초기값은 '방문자', 고정 아님)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자"

# [요구사항 7] 한국어 고정 및 한자/중국어 절대 차단 명령
KOREAN_PROTECT = "반드시 순수 한국어로만 답변하고, 한자(漢字)나 중국어를 절대 사용하지 마세요. 모든 설명은 한글로만 합니다."

persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 코딩 선생님이야. {st.session_state.user_name}님에게 한국어로만 쉽게 설명해줘. {KOREAN_PROTECT}",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 개인 비서야. 한국어로만 업무를 도와줘. {KOREAN_PROTECT}",
    "🎭 실시간 역할 변신": f"너는 역할극 전문가야. {st.session_state.user_name}님이 원하는 인물로 한국어 대화해. {KOREAN_PROTECT}",
    "🎲 운빨 테스트": f"너는 예언가야. {st.session_state.user_name}님의 운세를 재미있게 한국어로만 말해줘. {KOREAN_PROTECT}"
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 사이드바 (사용자 이름 변경 가능)
with st.sidebar:
    st.markdown("<h1 style='color:#1e3c72;'>⚡ 번개 대시보드</h1>", unsafe_allow_html=True)
    # 여기서 입력한 이름이 즉시 반영됨
    st.session_state.user_name = st.text_input("👤 당신의 이름", value=st.session_state.user_name)
    st.divider()
    selected = st.radio("모드 선택", list(persona_base.keys()), index=list(persona_base.keys()).index(st.session_state.current_mode))
    
    if selected != st.session_state.current_mode:
        st.session_state.current_mode = selected
        st.rerun()
    
    st.divider()
    if st.button("🗑️ 전체 대화 삭제"):
        st.session_state.multi_chat_history[selected] = []
        st.rerun()

# 메인 화면
messages = st.session_state.multi_chat_history[selected]
# 이름 변경 실시간 업데이트 로직
system_msg = {"role": "system", "content": persona_base[selected]}
if not messages or messages[0]["role"] != "system":
    messages.insert(0, system_msg)
else:
    messages[0] = system_msg

st.markdown(f'<div class="main-title">⚡ {selected}</div>', unsafe_allow_html=True)

for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# [요구사항 6 강조] 입력창 및 이름 레이블
st.markdown(f'<span class="dynamic-user-label">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("메시지를 입력해 주세요!"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if selected == "🎲 운빨 테스트":
            luck = random.randint(1, 100)
            st.write(f"🌌 {st.session_state.user_name}님의 에너지를 읽고 있습니다...")
            pb = st.progress(0); [ (time.sleep(0.005), pb.progress(i+1)) for i in range(100) ]
            st.markdown(f"### ⚡ 오늘의 번개 지수: **{luck}%**")
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{st.session_state.user_name}님의 행운 {luck}% 리액션을 한자 없이 한국어로만 해줘."}],
                temperature=0.0, # 한자 원천 차단
                stream=True
            )
            res = st.write_stream((chunk.choices[0].delta.content or "") for chunk in stream)
            if luck >= 90: st.balloons()
            messages.append({"role": "assistant", "content": f"운빨: {luck}% - {res}"})
        else:
            placeholder = st.empty(); full_ans = ""
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.0, # 논리 정연한 한국어 고정
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_ans += content
                    placeholder.markdown(full_ans + "▌")
            placeholder.markdown(full_ans)
            messages.append({"role": "assistant", "content": full_ans})