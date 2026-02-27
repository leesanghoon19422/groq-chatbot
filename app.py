import streamlit as st
from groq import Groq
import random
import time

# 1. [요구사항] 페이지 설정: 명칭은 '번개 챗봇 AI', 메뉴는 'expanded'로 항상 열어둠
st.set_page_config(
    page_title="번개 챗봇 AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded" 
)

# 2. [요구사항] 프리미엄 그라데이션 UI 디자인 (CSS)
# PC 상단 잘림 방지(12rem), 화이트/블루/퍼플 그라데이션, 모바일 최적화 고정
st.markdown("""
    <style>
    /* 전체 배경: 밋밋한 흰색이 아닌 고급스러운 소프트 그라데이션 */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%) !important;
        background-attachment: fixed !important;
        color: #2d3748 !important;
    }
    
    /* [핵심 요구사항] PC 상단 잘림 완벽 방지: 패딩 12rem 확보 */
    .block-container {
        max-width: 850px;
        padding-top: 12rem !important; 
        padding-bottom: 7rem;
    }

    /* 채팅 카드: 애플 스타일의 부드러운 그림자와 유리 질감 */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 25px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 15px 45px rgba(0,0,0,0.03) !important;
        margin-bottom: 30px;
        padding: 1.8rem !important;
    }

    /* 사이드바 디자인: 화이트톤의 깔끔한 스타일 */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #edf2f7 !important;
    }

    /* [요구사항] 버튼 스타일: 모바일에서도 시원한 크기, 화려한 그라데이션 */
    .stButton>button {
        width: 100% !important;
        height: 5.2rem !important;
        border-radius: 22px !important;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%) !important;
        color: white !important;
        font-weight: 900 !important;
        font-size: 1.4rem !important;
        border: none !important;
        box-shadow: 0 8px 30px rgba(37, 117, 252, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    }
    .stButton>button:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px rgba(37, 117, 252, 0.4) !important;
    }

    /* [요구사항] 가변형 사용자 이름 레이블: 입력창 상단에 선명하게 표시 */
    .user-dynamic-name-tag {
        font-size: 1.25rem;
        color: #1a365d;
        font-weight: 900;
        margin-bottom: 15px;
        display: block;
        border-left: 8px solid #2575fc;
        padding-left: 18px;
        background: rgba(37, 117, 252, 0.05);
        padding-top: 8px;
        padding-bottom: 8px;
        border-radius: 0 10px 10px 0;
    }

    /* [요구사항] 메인 타이틀: 그라데이션과 그림자 효과 */
    .premium-main-title {
        font-size: 3.5rem;
        font-weight: 950;
        text-align: center;
        background: linear-gradient(to right, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4rem;
        filter: drop-shadow(0 5px 15px rgba(0,0,0,0.1));
    }
    
    /* 하단 채팅창 컨테이너 위치 조정 */
    .stChatInputContainer {
        padding-bottom: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. API 보안 설정
try:
    # streamlit의 secrets 기능을 사용하여 API 키를 안전하게 불러옵니다.
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("🚨 .streamlit/secrets.toml 파일에 'GROQ_API_KEY'가 설정되어 있는지 확인해주세요.")
    st.stop()

# 4. [요구사항] 세션 상태 (사용자 이름은 고정값이 아니며, 방문자가 직접 수정 가능)
if "user_name" not in st.session_state:
    st.session_state.user_name = "방문자"

# 5. [핵심 요구사항] 페르소나 및 한자/중국어 박멸 규칙 (Strict Rule)
# 모델이 한자를 단 하나라도 쓰면 안 된다는 것을 시스템 차원에서 강제합니다.
HANJA_KILLER_PROMPT = """
[절대 규칙: 한자(漢字) 및 중국어 금지]
1. 답변에 단 한 글자의 한자도 포함하지 마세요. (예: 變身 -> 변신, 偉人 -> 위인으로만 표기)
2. 중국어 말투나 한자어투를 피하고 자연스러운 현대 한국어로만 답변하세요.
3. 한국어 답변 끝에 이상한 문자열이나 코드를 붙이지 마세요.
"""

persona_base = {
    "👨‍🏫 코딩 선생님": f"너는 코딩 선생님이야. {st.session_state.user_name}님에게 한국어로만 지식을 전해줘. {HANJA_KILLER_PROMPT}",
    "💼 번개 비서": f"너는 {st.session_state.user_name}님의 만능 비서야. 신속하게 한국어로 업무를 도와줘. {HANJA_KILLER_PROMPT}",
    "🎭 실시간 역할 변신": f"너는 역할극 전문가야. {st.session_state.user_name}님이 정해준 인물이 되어 한국어로만 대화해. {HANJA_KILLER_PROMPT}",
    "🎲 운빨 테스트": f"너는 신통방통한 예언가야. {st.session_state.user_name}님의 운세를 유쾌한 한국어 리액션으로 알려줘. {HANJA_KILLER_PROMPT}"
}

if "multi_chat_history" not in st.session_state:
    st.session_state.multi_chat_history = {mode: [] for mode in persona_base.keys()}
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "👨‍🏫 코딩 선생님"

# 6. [요구사항] 사이드바 메뉴 (첫 요구사항 명칭 '번개 챗봇 AI' 복구)
with st.sidebar:
    st.markdown("<h1 style='color:#2575fc; font-size: 2.2rem; font-weight:900;'>⚡ 번개 챗봇 AI</h1>", unsafe_allow_html=True)
    st.divider()
    # 사용자 이름 입력창 (가변형 이름 시스템의 시작)
    st.session_state.user_name = st.text_input("👤 당신의 이름을 알려주세요", value=st.session_state.user_name)
    st.divider()
    
    # 모드 선택 라디오 버튼
    selected = st.radio(
        "기능 모드 전환", 
        list(persona_base.keys()), 
        index=list(persona_base.keys()).index(st.session_state.current_mode)
    )
    
    # 모드 변경 시 화면 갱신
    if selected != st.session_state.current_mode:
        st.session_state.current_mode = selected
        st.rerun()
    
    st.divider()
    # [요구사항] 기능별(모드별) 삭제 버튼
    if st.button(f"🗑️ {selected} 기록 삭제"):
        st.session_state.multi_chat_history[selected] = []
        st.rerun()
    
    st.caption(f"접속자: {st.session_state.user_name} | 프리미엄 에디션")

# 7. 메인 화면 출력부
messages = st.session_state.multi_chat_history[selected]

# 실시간으로 변경된 이름을 시스템 프롬프트에 동적 반영
current_system_content = persona_base[selected]
if not messages or messages[0]["role"] != "system":
    messages.insert(0, {"role": "system", "content": current_system_content})
else:
    messages[0]["content"] = current_system_content

# 타이틀 출력
st.markdown(f'<div class="premium-main-title">⚡ {selected}</div>', unsafe_allow_html=True)

# 기존 대화 렌더링
for msg in messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 8. [요구사항] 입력창 영역 및 가변 이름 레이블
st.markdown(f'<span class="user-dynamic-name-tag">👤 {st.session_state.user_name}님의 메시지</span>', unsafe_allow_html=True)
if prompt := st.chat_input("이곳에 질문하거나 요청하세요! ⚡"):
    # 사용자 메시지 저장 및 출력
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 답변 생성부
    with st.chat_message("assistant"):
        # [핵심 요구사항] 한자 방지를 위해 Temperature 0.0 고정 (가장 안전한 한국어 선택)
        if selected == "🎲 운빨 테스트":
            luck = random.randint(1, 100)
            st.write(f"🌠 {st.session_state.user_name}님의 운세를 번개처럼 계산 중...")
            pb = st.progress(0)
            for i in range(100):
                time.sleep(0.006)
                pb.progress(i + 1)
            
            st.markdown(f"### ⚡ 오늘의 행운 점수: **{luck}%**")
            
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{st.session_state.user_name}님의 행운 {luck}%에 대해 '한자 절대 없이' 한국어로만 아주 길게 리액션해줘."}],
                temperature=0.0,
                stream=True
            )
            res = st.write_stream((chunk.choices[0].delta.content or "") for chunk in stream)
            if luck >= 90: st.balloons()
            messages.append({"role": "assistant", "content": f"운세 점수: {luck}% - {res}"})
        
        else:
            placeholder = st.empty()
            full_ans = ""
            try:
                # 스트리밍 답변 생성
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.0, # 한자 오염 방지를 위한 결정적 출력
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
                st.error(f"⚠️ 연결 오류가 발생했습니다: {e}")