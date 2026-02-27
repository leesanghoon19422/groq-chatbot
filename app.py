import streamlit as st
from groq import Groq
import random
import time

# 1. [요구사항] 페이지 설정: 명칭 고정 및 메뉴 상시 열림
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# 2. [요구사항] 초강력 프리미엄 UI 디자인 (CSS)
# 배경, 버튼, 말풍선 모두에 그라데이션과 입체감을 주었습니다.
st.markdown("""
    <style>
    /* 1. 전체 배경: 움직이는 듯한 세련된 그라데이션 고정 */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        background-attachment: fixed !important;
        color: #ffffff !important;
    }

    /* 2. PC 상단 잘림 방지: 13rem으로 극대화하여 절대 안 가려지게 설정 */
    .block-container {
        max-width: 850px;
        padding-top: 13rem !important; 
        padding-bottom: 5rem;
        background: rgba(255, 255, 255, 0.05); /* 본문 영역 살짝 밝게 */
        border-radius: 30px;
    }

    /* 3. 채팅 말풍선: 반투명 유리 질감(Glassmorphism) 적용 */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2) !important;
        margin-bottom: 25px !important;
        color: white !important;
    }
    
    /* 채팅 텍스트 색상 강제 흰색 고정 */
    .stChatMessage p, .stChatMessage div {
        color: white !important;
        font-size: 1.1rem !important;
    }

    /* 4. 사이드바(메뉴): 다크 그린-블루 계열로 고급스럽게 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* 5. [핵심] 버튼 디자인: 네온 블루 그라데이션 및 애니메이션 효과 */
    .stButton>button {
        width: 100% !important;
        height: 5.5rem !important;
        border-radius: 25px !important;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 1.5rem !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 10px 25px rgba(0, 210, 255, 0.4) !important;
        transition: all 0.4s ease !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.02) !important;
        box-shadow: 0 15px 35px rgba(0, 210, 255, 0.6) !important;
        filter: brightness(1.1);
    }

    /* 6. 사용자 이름 레이블: 입력창 위에 플로팅 느낌으로 배치 */
    .dynamic-user-label {
        font-size: 1.3rem;
        color: #00d2ff;
        font-weight: 900;
        margin-bottom: 15px;
        display: block;
        padding-left: 20px;
        border-left: 10px solid #00d2ff;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.5);
    }

    /* 7. 메인 타이틀: 무지개빛 그라데이션 텍스트 */
    .super-main-title {
        font-size: 3.8rem;
        font-weight: 950;
        text-align: center;
        background: linear-gradient(to right, #00d2ff, #3a7bd5, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4rem;
        filter: drop-shadow(0 5px 15px rgba(0,0,0,0.2));
        animation: gradient-text 3s infinite;
    }

    /* 채팅 입력창 배경 조절 */
    .stChatInputContainer {
        background: transparent !important;
        padding-bottom: 60px;
    }
    .stChatInput input {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 20px !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 보안 설정
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 API 키를 등록해주세요!")
    st.stop()

# 4. 세션 상태 (방문자 이름 가변형)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자"

# 5. [요구사항] 페르소나 및 한자 완벽 박멸 지침
# AI 답변 생성 시 한자를 쓰지 않도록 강력하게 제어합니다.
STRICT_KOREAN_ONLY = "한자(漢字)와 중국어를 절대 사용하지 마세요. 반드시 순수 한글로만 대화하세요."

persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 코딩 선생님이야. {st.session_state.user_name}님에게 한글로만 쉽게 알려줘. {STRICT_KOREAN_ONLY}",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 비서야. 한글로 업무를 도와줘. {STRICT_KOREAN_ONLY}",
    "🎭 실시간 역할 변신": f"너는 역할극 전문가야. {st.session_state.user_name}님이 정해준 인물로 한글 대화해. {STRICT_KOREAN_ONLY}",
    "🎲 운빨 테스트": f"너는 예언가야. {st.session_state.user_name}님의 점수를 한글 리액션으로 말해줘. {STRICT_KOREAN_ONLY}"
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. [요구사항] 사이드바 (명칭: 번개 챗봇 AI)
with st.sidebar:
    st.markdown("<h1 style='color:#00d2ff; font-size: 2.2rem; font-weight:900;'>⚡ 번개 챗봇 AI</h1>", unsafe_allow_html=True)
    st.session_state.user_name = st.text_input("👤 이름 입력", value=st.session_state.user_name)
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

# 7. 메인 화면 렌더링
messages = st.session_state.multi_chat_history[selected]
system_msg = {"role": "system", "content": persona_base[selected]}
if not messages or messages[0]["role"] != "system":
    messages.insert(0, system_msg)
else:
    messages[0] = system_msg

st.markdown(f'<div class="super-main-title">⚡ {selected}</div>', unsafe_allow_html=True)

for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. 입력 영역 (가변 이름 레이블)
st.markdown(f'<span class="dynamic-user-label">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("여기에 입력하고 번개를 누르세요! ⚡"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 한자 차단을 위해 temperature 0.0 고정
        if selected == "🎲 운빨 테스트":
            luck = random.randint(1, 100)
            st.write(f"🌠 {st.session_state.user_name}님의 기운을 읽고 있습니다...")
            pb = st.progress(0); [ (time.sleep(0.005), pb.progress(i+1)) for i in range(100) ]
            st.markdown(f"### ⚡ 오늘의 점수: **{luck}%**")
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{st.session_state.user_name}님의 점수 {luck}%에 대해 한자 없이 한국어로만 리액션해줘."}],
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
                st.error(f"오류: {e}")