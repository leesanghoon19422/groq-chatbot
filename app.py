import streamlit as st
from groq import Groq
import random
import time

# 1. 페이지 설정: 메뉴 자동 열림 및 타이틀 설정
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# 2. 고품격 그라데이션 UI 디자인 (CSS)
# 모든 요소에 !important를 붙여 스타일이 변하지 않도록 고정했습니다.
st.markdown("""
    <style>
    /* 전체 배경: 은은하고 세련된 블루-퍼플 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4eefe 100%) !important;
        color: #2d3748 !important;
    }
    
    /* PC 상단 잘림 방지: 12rem 여백 확보 */
    .block-container {
        max-width: 850px;
        padding-top: 12rem !important; 
        padding-bottom: 7rem;
    }

    /* 채팅 말풍선: 투명도가 있는 유리 느낌(Glassmorphism)과 그라데이션 테두리 */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        margin-bottom: 25px;
        padding: 1.5rem;
    }

    /* 사이드바(메뉴) 디자인: 사이드바 자체에도 그라데이션 적용 */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(180deg, #ffffff 0%, #f0f4f8 100%) !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    /* 사이드바 내부 입력창/라디오 버튼 스타일링 */
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #d1d5db !important;
    }

    /* 버튼 스타일: 강렬한 블루-인디고 그라데이션 및 입체 효과 */
    .stButton>button {
        width: 100% !important;
        height: 4.8rem !important;
        border-radius: 20px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(118, 75, 162, 0.4) !important;
    }

    /* 사용자 이름 레이블: 네온 블루 포인트 적용 */
    .user-dynamic-label {
        font-size: 1.1rem;
        color: #4a5568;
        font-weight: 800;
        margin-bottom: 12px;
        display: block;
        border-left: 6px solid #667eea;
        padding-left: 15px;
    }

    /* 메인 타이틀: 텍스트 그라데이션 적용 */
    .main-header-gradient {
        font-size: 3.2rem;
        font-weight: 950;
        text-align: center;
        background: linear-gradient(to right, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 3rem;
        letter-spacing: -2px;
    }
    
    /* 하단 입력창 고정 및 여백 */
    .stChatInputContainer {
        padding-bottom: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 연결
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 API 키 설정 확인이 필요합니다!")
    st.stop()

# 4. 세션 상태 (방문자 이름 설정)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자"

# 5. 페르소나 설정 (한자/중국어 절대 차단용 물리적 가이드라인)
# AI가 한자를 쓰면 안 된다는 것을 인식하도록 강력한 경고를 포함했습니다.
STRICT_KOREAN_GUIDE = "모든 답변은 한자(漢字)를 절대 섞지 말고 순수 한글로만 작성하세요. 중국어 말투나 한자 단어를 쓰지 마세요."

persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 아주 유능한 코딩 선생님이야. {st.session_state.user_name}님에게 한글로만 쉽게 설명해줘. {STRICT_KOREAN_GUIDE}",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 전문 비서야. 모든 업무를 한글로만 신속하게 도와줘. {STRICT_KOREAN_GUIDE}",
    "🎭 실시간 역할 변신": f"너는 역할극 전문가야. {st.session_state.user_name}님이 원하는 배역이 되어 한글로만 대화해. {STRICT_KOREAN_GUIDE}",
    "🎲 운빨 테스트": f"너는 신비로운 예언가야. {st.session_state.user_name}님의 운세를 유쾌한 한글 리액션으로 알려줘. {STRICT_KOREAN_GUIDE}"
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. 사이드바 (메뉴 디자인 및 이름 입력)
with st.sidebar:
    st.markdown("<h1 style='color:#4a5568; font-size: 1.8rem;'>⚡ 번개 Dashboard</h1>", unsafe_allow_html=True)
    st.session_state.user_name = st.text_input("👤 사용자 이름 설정", value=st.session_state.user_name)
    st.divider()
    
    selected = st.radio(
        "기능 모드 선택", 
        list(persona_base.keys()), 
        index=list(persona_base.keys()).index(st.session_state.current_mode)
    )
    
    if selected != st.session_state.current_mode:
        st.session_state.current_mode = selected
        st.rerun()
    
    st.divider()
    # [요구사항 반영] 각 기능 이름에 맞는 삭제 버튼
    if st.button(f"🗑️ {selected} 기록 삭제"):
        st.session_state.multi_chat_history[selected] = []
        st.rerun()
    st.caption("Ver 8.0 Premium Edition")

# 7. 메인 화면 렌더링
messages = st.session_state.multi_chat_history[selected]
# 시스템 프롬프트에 실시간 이름 및 규칙 적용
system_msg = {"role": "system", "content": persona_base[selected]}
if not messages or messages[0]["role"] != "system":
    messages.insert(0, system_msg)
else:
    messages[0] = system_msg

# 그라데이션 타이틀 출력
st.markdown(f'<div class="main-header-gradient">⚡ {selected}</div>', unsafe_allow_html=True)

for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. 입력 영역 및 가변 이름 레이블
st.markdown(f'<span class="user-dynamic-label">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("메시지를 입력해 보세요! ⚡"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 한자 차단을 위해 Temperature를 0.0으로 설정
        if selected == "🎲 운빨 테스트":
            luck = random.randint(1, 100)
            st.write(f"🌌 {st.session_state.user_name}님의 운세를 계산 중...")
            pb = st.progress(0); [ (time.sleep(0.005), pb.progress(i+1)) for i in range(100) ]
            st.markdown(f"### ⚡ 오늘의 행운 지수: **{luck}%**")
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{st.session_state.user_name}님의 점수 {luck}%에 대해 한자 없이 유쾌한 한글로만 리액션해줘."}],
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