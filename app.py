import streamlit as st
from groq import Groq
import random
import time

# 1. 페이지 설정: 메뉴 상시 열림(expanded) 및 레이아웃 최적화
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# 2. 최상급 프리미엄 UI 디자인 (CSS)
# PC 상단 잘림 방지, 모바일 터치 최적화, 다크모드 배제(화이트톤)
st.markdown("""
    <style>
    /* 전체 배경: 깨끗하고 세련된 화이트 파스텔 그라데이션 */
    .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f0f7ff 100%);
        color: #1a202c;
    }
    
    /* PC 화면 상단 잘림 방지: padding-top을 8rem으로 매우 넉넉히 확보 */
    .block-container {
        max-width: 800px;
        padding-top: 8rem !important; 
        padding-bottom: 7rem;
    }

    /* 채팅 말풍선: 애플 스타일의 카드 디자인 */
    .stChatMessage {
        background-color: white !important;
        border-radius: 20px !important;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        padding: 1.5rem;
    }

    /* 사이드바(메뉴): 고급스러운 블러 효과 적용 */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-right: 1px solid #edf2f7;
    }

    /* 버튼 스타일: 모바일에서 누르기 편하게 큼직하고 화려한 블루 그라데이션 */
    .stButton>button {
        width: 100%;
        height: 4.2rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        font-weight: 800;
        font-size: 1.2rem;
        border: none;
        box-shadow: 0 4px 15px rgba(58, 123, 213, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(58, 123, 213, 0.4);
    }

    /* 사용자 이름 레이블: 입력창 바로 위에 사용자가 설정한 이름 표시 */
    .dynamic-name-label {
        font-size: 1.1rem;
        color: #1e3c72;
        font-weight: 800;
        margin-bottom: 12px;
        display: block;
        padding-left: 5px;
        border-left: 5px solid #00d2ff;
        padding-left: 15px;
    }

    /* 메인 타이틀: 세련된 타이포그래피 */
    .main-header-title {
        font-size: 2.6rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(to right, #1e3c72, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2.5rem;
    }
    
    /* 하단 입력창 여백 고정 */
    .stChatInputContainer {
        padding-bottom: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 보안 연결
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 .streamlit/secrets.toml 파일에 GROQ_API_KEY를 설정해주세요!")
    st.stop()

# 4. 사용자 세션 상태 (이름은 고정하지 않고 방문자가 직접 수정 가능)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자"

# 5. 페르소나 설정 (순수 한국어 강력 고정 및 한자 사용 금지 명령)
KOREAN_STRICT_RULE = "반드시 순수 한국어로만 답변하고, 한자(漢字)나 중국어 단어를 절대 섞지 마세요. 문장 끝에 이상한 코드를 붙이지 마세요."

persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 세계 최고의 코딩 선생님이야. {st.session_state.user_name}님에게 아주 쉽게 한국어로만 가르쳐줘. {KOREAN_STRICT_RULE}",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 만능 비서야. 신속하고 정확하게 한국어로만 답변해. {KOREAN_STRICT_RULE}",
    "🎭 실시간 역할 변신": f"너는 {st.session_state.user_name}님이 지정하는 인물로 즉시 변신해. 개성을 살려 한국어로만 대화해. {KOREAN_STRICT_RULE}",
    "🎲 운빨 테스트": f"너는 {st.session_state.user_name}님의 오늘 운세를 점치는 예언가야. 아주 유쾌하게 한국어로만 리액션해. {KOREAN_STRICT_RULE}"
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. 사이드바 메뉴 (기본 오픈 상태)
with st.sidebar:
    st.markdown("<h2 style='color:#1e3c72;'>⚡ 번개 컨트롤러</h2>", unsafe_allow_html=True)
    # 상훈으로 고정되지 않고 사용자가 직접 입력하는 이름 반영
    st.session_state.user_name = st.text_input("👤 당신의 이름을 입력하세요", value=st.session_state.user_name)
    st.divider()
    
    selected = st.radio(
        "기능 모드 전환", 
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
    st.caption("최고의 안정성과 속도를 제공합니다.")

# 7. 대화 로직 및 화면 렌더링
messages = st.session_state.multi_chat_history[selected]

# 실시간 이름 변경을 시스템 프롬프트에 반영
system_msg = {"role": "system", "content": persona_base[selected]}
if not messages or messages[0]["role"] != "system":
    messages.insert(0, system_msg)
else:
    messages[0] = system_msg

# 메인 타이틀 출력
st.markdown(f'<div class="main-header-title">⚡ {selected}</div>', unsafe_allow_html=True)

for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. 입력창 영역 (가변형 이름 레이블 포함)
st.markdown(f'<span class="dynamic-name-label">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("이곳에 질문이나 요청을 입력하세요 ⚡"):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if selected == "🎲 운빨 테스트":
            luck = random.randint(1, 100)
            st.write(f"🌌 {st.session_state.user_name}님의 기운을 분석하는 중...")
            pb = st.progress(0)
            for i in range(100):
                time.sleep(0.005)
                pb.progress(i + 1)
            
            st.markdown(f"### ⚡ 오늘의 번개 행운 지수: **{luck}%**")
            
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{st.session_state.user_name}님의 행운 {luck}% 리액션 순수 한국어로만 해줘."}],
                temperature=0.3, # 한자 발생 억제를 위해 낮게 설정
                stream=True
            )
            res = st.write_stream((chunk.choices[0].delta.content or "") for chunk in stream)
            if luck >= 90: st.balloons()
            messages.append({"role": "assistant", "content": f"운빨 결과: {luck}% - {res}"})
        
        else:
            placeholder = st.empty()
            full_ans = ""
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.0, # 가장 논리적이고 순수한 한국어 답변 유도
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
                st.error(f"서버 응답 오류: {e}")