import streamlit as st
from groq import Groq
import random
import time

# 1. 페이지 설정: 메뉴 자동 열림('expanded') 및 레이아웃 최적화
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# 2. 고품질 비주얼 디자인 (CSS)
st.markdown("""
    <style>
    /* 배경: 세련된 소프트 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #1a202c;
    }
    
    /* PC 상단 잘림 완벽 방지: 여백을 7rem으로 넉넉히 확보 */
    .block-container {
        max-width: 850px;
        padding-top: 7rem !important; 
        padding-bottom: 7rem;
    }

    /* 채팅 메시지: 부드러운 그림자와 둥근 모서리의 화이트 카드 */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 25px !important;
        border: none;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        padding: 1.5rem;
    }

    /* 사이드바 스타일: 유리창 같은 블러 효과(Glassmorphism) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* 버튼 스타일: 시선을 사로잡는 선명한 그라데이션 */
    .stButton>button {
        width: 100%;
        height: 4rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        font-weight: 800;
        font-size: 1.2rem;
        border: none;
        box-shadow: 0 4px 15px rgba(58, 123, 213, 0.3);
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(58, 123, 213, 0.4);
    }

    /* 이름 레이블: 입력창 위에서 사용자를 명확히 안내 */
    .dynamic-user-label {
        font-size: 1rem;
        color: #2d3748;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .dynamic-user-label::before {
        content: '⚡';
        color: #3a7bd5;
    }

    /* 메인 타이틀 애니메이션 느낌 */
    .premium-header {
        font-size: 2.5rem;
        font-weight: 900;
        text-align: center;
        background: -webkit-linear-gradient(#2d3748, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    /* 입력창 하단 위치 조정 */
    .stChatInputContainer {
        padding-bottom: 40px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 보안 설정
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 .streamlit/secrets.toml에 API 키가 필요합니다!")
    st.stop()

# 4. 세션 상태 (사용자 이름 설정: 고정값 아님)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자" # 초기값만 설정

# 5. 페르소나 설정 (입력된 이름을 실시간 반영)
persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 코딩 선생님이야. {st.session_state.user_name}님에게 한국어로만 친절히 설명해줘.",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 비서야. 한국어로만 모든 업무를 도와줘.",
    "🎭 실시간 역할 변신": f"너는 {st.session_state.user_name}님이 원하는 역할로 변신해. 그 말투로 한국어 대화해.",
    "🎲 운빨 테스트": f"너는 {st.session_state.user_name}님의 운을 점치는 예언가야. 한국어로만 결과 리액션해."
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. 사이드바 (메뉴 열림 상태 유지 및 이름 입력)
with st.sidebar:
    st.markdown("<h1 style='font-size: 1.5rem;'>⚡ 번개 컨트롤</h1>", unsafe_allow_html=True)
    # 상훈으로 고정하지 않고 여기서 입력한 값이 바로 반영됨
    st.session_state.user_name = st.text_input("👤 당신의 이름을 알려주세요", value=st.session_state.user_name)
    st.divider()
    
    selected = st.radio(
        "기능 모드", 
        list(persona_base.keys()), 
        index=list(persona_base.keys()).index(st.session_state.current_mode)
    )
    
    if selected != st.session_state.current_mode:
        st.session_state.current_mode = selected
        st.rerun()
        
    st.divider()
    if st.button(f"🗑️ {selected} 기록 초기화"):
        st.session_state.multi_chat_history[selected] = []
        st.rerun()
    st.caption(f"접속 중: {st.session_state.user_name}")

# 7. 메인 화면 출력
messages = st.session_state.multi_chat_history[selected]
# 이름이 변경될 수 있으므로 시스템 프롬프트를 매번 최신화
system_content = persona_base[selected]
if not messages or messages[0]["role"] != "system":
    messages.insert(0, {"role": "system", "content": system_content})
else:
    messages[0]["content"] = system_content # 이름 변경 반영

st.markdown(f'<div class="premium-header">⚡ {selected}</div>', unsafe_allow_html=True)

for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. 입력창 및 다이내믹 이름 레이블
st.markdown(f'<div class="dynamic-user-label">{st.session_state.user_name}님의 메시지</div>', unsafe_allow_html=True)
if prompt := st.chat_input("이곳에 입력하고 번개처럼 답변받으세요! ⚡"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if selected == "🎲 운빨 테스트":
            luck = random.randint(1, 100)
            st.write(f"🌠 {st.session_state.user_name}님의 기운을 모으는 중...")
            bar = st.progress(0)
            for i in range(100):
                time.sleep(0.005)
                bar.progress(i + 1)
            st.markdown(f"### ⚡ 오늘의 번개 행운: **{luck}%**")
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{st.session_state.user_name}님의 행운 {luck}%에 대해 한국어로 리액션해줘."}],
                temperature=0.7,
                stream=True
            )
            res = st.write_stream((chunk.choices[0].delta.content or "") for chunk in stream)
            if luck >= 90: st.balloons()
            messages.append({"role": "assistant", "content": f"운빨: {luck}% - {res}"})
        else:
            placeholder = st.empty()
            full_ans = ""
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.1,
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