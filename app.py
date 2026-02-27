import streamlit as st
from groq import Groq
import random
import time

# 1. 페이지 설정: PC와 모바일 모두에서 메뉴가 기본으로 닫혀있어 넓은 화면 제공
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. 통합 반응형 UI 디자인 (CSS)
st.markdown("""
    <style>
    /* 전체 배경: 깨끗하고 밝은 화이트 파스텔 그라데이션 */
    .stApp {
        background: linear-gradient(180deg, #f8fbff 0%, #e8f1f9 100%);
        color: #333;
    }
    
    /* PC와 모바일에서 모두 보기 편하도록 본문 컨테이너 너비 제한 및 중앙 정렬 */
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* 채팅 말풍선: 깔끔하고 고급스러운 화이트 카드 스타일 */
    .stChatMessage {
        background-color: white !important;
        border-radius: 20px !important;
        border: 1px solid #e1e8ed;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 15px;
        padding: 15px;
    }

    /* 사이드바(메뉴): 깔끔한 화이트 디자인 */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #f0f0f0;
    }

    /* 버튼 스타일: 클릭하고 싶게 만드는 화려한 블루 그라데이션 */
    .stButton>button {
        width: 100%;
        height: 3.5rem;
        border-radius: 15px;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        border: none;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.3);
    }

    /* 사용자 입력창 바로 위의 이름 레이블 (상훈님의 요청사항) */
    .user-name-label {
        font-size: 0.9rem;
        color: #4facfe;
        font-weight: 800;
        margin-bottom: 8px;
        display: block;
        padding-left: 5px;
    }

    /* 메인 타이틀: 세련된 폰트와 컬러 */
    .main-header {
        font-size: 2rem;
        font-weight: 900;
        text-align: center;
        color: #1e3c72;
        margin-bottom: 1.5rem;
        letter-spacing: -1px;
    }
    
    /* 입력창 위치 최적화 */
    .stChatInputContainer {
        padding-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 키 보안 연결
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 .streamlit/secrets.toml 파일에 API 키(GROQ_API_KEY)를 설정해주세요!")
    st.stop()

# 4. 세션 상태 관리 (이름 저장)
if "user_name" not in st.session_state:
    st.session_state.user_name = "사용자"

# 5. 페르소나 정의 (한국어 답변 강력 고정)
persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 아주 친절하고 자상한 코딩 선생님이야. {st.session_state.user_name}님에게 비유를 들어 한국어로만 설명해줘. 절대 외국어나 의미 없는 코드를 답변 끝에 붙이지 마.",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 유능한 개인 비서야. 모든 요청을 번개처럼 한국어로만 처리해줘. 깔끔하고 명확하게 답변해.",
    "🎭 실시간 역할 변신": f"너는 {st.session_state.user_name}님이 부여하는 어떤 역할이든 즉시 수락해. 말투는 그 인물처럼 하되, 반드시 한국어로만 대화해야 해.",
    "🎲 운빨 테스트": f"너는 {st.session_state.user_name}님의 운세를 봐주는 유쾌한 점술가야. 결과 수치에 따라 익살스럽고 호들갑스럽게 한국어로만 말해줘."
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. 사이드바(메뉴) 구성: 열고 닫기 쉽고 직관적인 배치
with st.sidebar:
    st.markdown("### ⚡ 번개 대시보드")
    st.session_state.user_name = st.text_input("👤 사용자 이름", value=st.session_state.user_name)
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
    if st.button(f"🗑️ 현재 모드 대화 삭제"):
        st.session_state.multi_chat_history[selected] = []
        st.rerun()
    st.caption("메뉴를 닫으려면 상단 화살표를 누르세요.")

# 7. 대화 로직 실행
messages = st.session_state.multi_chat_history[selected]

# 시스템 프롬프트 주입
if not any(m["role"] == "system" for m in messages):
    messages.insert(0, {"role": "system", "content": persona_base[selected]})

# 메인 헤더 표시
st.markdown(f'<div class="main-header">⚡ {selected}</div>', unsafe_allow_html=True)
st.write(f"반가워요, **{st.session_state.user_name}님**! 무엇을 도와드릴까요?")

# 이전 대화 출력
for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. 사용자 입력 영역 (이름 레이블 포함)
st.markdown(f'<span class="user-name-label">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("이곳에 질문을 입력하세요..."):
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 운빨 테스트 특수 로직
        if selected == "🎲 운빨 테스트":
            luck_val = random.randint(1, 100)
            st.write("🌌 운명의 기운을 분석하는 중...")
            pb = st.progress(0)
            for i in range(100):
                time.sleep(0.005)
                pb.progress(i + 1)
            
            st.markdown(f"### ⚡ 오늘의 번개 행운 지수: **{luck_val}%**")
            
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"{st.session_state.user_name}님의 운빨이 {luck_val}%야. 한국어로만 아주 재밌게 리액션해줘."}],
                    temperature=0.7,
                    stream=True
                )
                res_text = st.write_stream((chunk.choices[0].delta.content or "") for chunk in stream)
                if luck_val >= 90: st.balloons()
                messages.append({"role": "assistant", "content": f"운빨 결과: {luck_val}% - {res_text}"})
            except Exception as e:
                st.error(f"오류: {e}")
        
        # 일반 대화 로직
        else:
            ans_placeholder = st.empty()
            full_ans = ""
            try:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.1, # 헛소리 방지를 위해 최저 온도로 설정
                    stream=True
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        full_ans += content
                        ans_placeholder.markdown(full_ans + "▌")
                ans_placeholder.markdown(full_ans)
                messages.append({"role": "assistant", "content": full_ans})
            except Exception as e:
                st.error(f"통신 에러: {e}")