import streamlit as st
from groq import Groq
import random
import time

# 1. 페이지 설정: 메뉴 상시 열림 및 레이아웃 고정
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# 2. 프리미엄 UI 디자인 고정 (CSS)
# PC 상단 여백 12rem 확보, 다크모드 무시 화이트 고정, 모바일 버튼 최적화
st.markdown("""
    <style>
    /* 배경 및 기본 텍스트 색상 강제 고정 */
    .stApp {
        background: #ffffff !important;
        background-image: linear-gradient(180deg, #ffffff 0%, #f4f9ff 100%) !important;
        color: #1a202c !important;
    }
    
    /* PC 상단 잘림 방지 여백 */
    .block-container {
        max-width: 800px;
        padding-top: 12rem !important; 
        padding-bottom: 7rem;
    }

    /* 채팅 카드 디자인 */
    .stChatMessage {
        background-color: #ffffff !important;
        border-radius: 25px !important;
        border: 1px solid #eef2f6 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        margin-bottom: 25px;
    }

    /* 사이드바 디자인 */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #f0f4f8 !important;
    }

    /* 버튼 스타일: 블루 그라데이션 및 모바일 크기 최적화 */
    .stButton>button {
        width: 100% !important;
        height: 5rem !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 1.3rem !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(58, 123, 213, 0.2) !important;
    }

    /* 사용자 이름 레이블 */
    .dynamic-label {
        font-size: 1.1rem;
        color: #1e3c72;
        font-weight: 900;
        margin-bottom: 15px;
        display: block;
        border-left: 8px solid #00d2ff;
        padding-left: 15px;
    }

    /* 메인 타이틀 */
    .main-title {
        font-size: 3rem;
        font-weight: 950;
        text-align: center;
        color: #1e3c72;
        margin-bottom: 3.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 보안 설정
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 API 키 설정이 필요합니다!")
    st.stop()

# 4. 세션 상태 (사용자 이름 가변형)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자"

# 5. 페르소나 설정 (한자/중국어 절대 금지 규칙 강화)
STRICT_KOREAN = "반드시 한글로만 답변하세요. 한자(漢字)나 중국어 표기를 절대 사용하지 마세요. 모든 단어는 순수 한국어로 번역해서 답변하세요."

persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 코딩 선생님이야. {st.session_state.user_name}님에게 한국어로만 쉽게 알려줘. {STRICT_KOREAN}",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 비서야. 한국어로만 업무를 도와줘. {STRICT_KOREAN}",
    "🎭 실시간 역할 변신": f"너는 역할극 전문가야. {st.session_state.user_name}님이 정해준 인물로 한국어로만 대화해. {STRICT_KOREAN}",
    "🎲 운빨 테스트": f"너는 예언가야. {st.session_state.user_name}님의 운세를 유쾌한 한국어로만 리액션해줘. {STRICT_KOREAN}"
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. 사이드바 (이름 입력 및 메뉴)
with st.sidebar:
    st.markdown("<h2 style='color:#1e3c72;'>⚡ 번개 메뉴</h2>", unsafe_allow_html=True)
    st.session_state.user_name = st.text_input("👤 당신의 이름", value=st.session_state.user_name)
    st.divider()
    selected = st.radio("모드 선택", list(persona_base.keys()), index=list(persona_base.keys()).index(st.session_state.current_mode))
    
    if selected != st.session_state.current_mode:
        st.session_state.current_mode = selected
        st.rerun()
    
    st.divider()
    # 상훈님 요청 사항: 각 기능 이름에 맞게 삭제 버튼 명칭 변경
    if st.button(f"🗑️ {selected} 기록 삭제"):
        st.session_state.multi_chat_history[selected] = []
        st.rerun()

# 7. 화면 출력
messages = st.session_state.multi_chat_history[selected]
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

# 8. 입력창 영역
st.markdown(f'<span class="dynamic-label">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("여기에 내용을 입력하세요! ⚡"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if selected == "🎲 운빨 테스트":
            luck = random.randint(1, 100)
            st.write(f"🌌 {st.session_state.user_name}님의 운세 분석 중...")
            pb = st.progress(0); [ (time.sleep(0.005), pb.progress(i+1)) for i in range(100) ]
            st.markdown(f"### ⚡ 오늘의 행운: **{luck}%**")
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{st.session_state.user_name}님의 운빨 {luck}% 리액션을 한글로만 해줘. 한자 절대 쓰지 마!"}],
                temperature=0.0,
                stream=True
            )
            res = st.write_stream((chunk.choices[0].delta.content or "") for chunk in stream)
            if luck >= 90: st.balloons()
            messages.append({"role": "assistant", "content": f"결과: {luck}% - {res}"})
        else:
            placeholder = st.empty(); full_ans = ""
            try:
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
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")