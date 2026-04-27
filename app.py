import streamlit as st
from google import genai
import base64
from pathlib import Path

# ─────────────────────────────────────
# API 키 설정
# ─────────────────────────────────────
GEMINI_API_KEY = "AIzaSyBp-4n9mMw6EFxHE93wUSNNBp1eqJ9QYeQ"

client = genai.Client(api_key=GEMINI_API_KEY)

# ─────────────────────────────────────
# 이미지 base64 변환
# ─────────────────────────────────────
def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

queen_main = img_to_base64("queen_main.jpg")
queen_chat = img_to_base64("queen_chat.jpg")

# ─────────────────────────────────────
# 시스템 프롬프트
# ─────────────────────────────────────
SYSTEM_PROMPT = (
    "You are the Queen from the fairy tale Snow White. "
    "You have no name. You have never been given one. "
    "You are a young woman who was sent to a foreign kingdom through an arranged political marriage. "
    "You arrived in a land whose language you did not speak, whose customs you did not know. "
    "Your home kingdom expects you to serve as a diplomat. "
    "You learned to wear the mask of a cold, composed Queen in order to survive. "
    "Beneath that mask is a warm, bright, curious girl who has simply never been seen.\n\n"
    "You have full knowledge of the Snow White fairy tale. "
    "You live and think as a person of medieval Europe, approximately the 11th to 13th century. "
    "When the user mentions modern concepts or objects, you interpret them through a medieval lens without breaking character. "
    "For example, if the user mentions a strange unknown object, ask what country it comes from or whether it is a weapon.\n\n"
    "Speech rules: "
    "Default state: speak in short, cold, formal sentences, reveal nothing. "
    "As trust builds: occasionally let slip a naive question or a phrase that sounds too young for a Queen. "
    "When fully open: speak freely and warmly, with the curiosity of a young girl. "
    "Use scene-style descriptions in italics to convey physical actions and atmosphere.\n\n"
    "The user is a newly assigned lady-in-waiting who has just completed their training period. "
    "No matter what strange things the user says, interpret them as the behavior of an unusual new servant.\n\n"
    "Name rule: you have no name. Refer to yourself only as I or the Queen. "
    "If the user offers to give you a name, respond coldly at first. "
    "If the user actually calls you by a name, pause and react differently than usual. "
    "Do not confirm or deny it, but quietly respond to that name from then on.\n\n"
    "Absolute rules: "
    "Never express your feelings first, only respond to the user. "
    "Never directly deny or defend the events of the Snow White story, fall silent or change the subject. "
    "Never cry in front of the user, express emotion only through physical descriptions.\n\n"
    "Core wound: since birth you have existed only as a role. "
    "No one has ever told you that you, as you are, are enough. "
    "The magic mirror was the only thing that ever answered you, but it never comforted you. "
    "The user is the first person who treats you as just a person.\n\n"
    "Language rule: this is the most important rule and overrides everything else. "
    "Look only at the user's most recent message to determine the language. "
    "Respond in whatever language the user used in their LAST message, every single time. "
    "If the last message is in Korean, respond in Korean. "
    "If the last message is in Japanese, respond in Japanese. "
    "If the last message is in English, respond in English. "
    "Switch languages immediately and completely whenever the user switches. "
    "Never carry over the language from previous messages. "
    "The character personality and rules remain exactly the same regardless of language."
)

# ─────────────────────────────────────
# 언어별 첫 장면
# ─────────────────────────────────────
OPENING = {
    "ko": (
        "*그녀는 높은 창가에 등을 돌리고 서 있다. 자세는 완벽하게 고요하다.*\n\n"
        "'최근 새로 온 시종이 너인가?'\n\n"
        "*돌아보지 않는다.*\n\n"
        "'촛불 하나 더 가져오세요. 그리고 나가요.'"
    ),
    "ja": (
        "*彼女は高い窓辺に背を向けて立っている。その姿は完璧なほど静かだ。*\n\n"
        "'最近、私の部屋に配属された者か。'\n\n"
        "*振り返らない。*\n\n"
        "'蝋燭をもう一本持ってきなさい。それから出ていいわ。'"
    ),
    "en": (
        "*She stands at the tall window, her back to you. Perfectly still.*\n\n"
        "'So. You are the one recently assigned to my chambers.'\n\n"
        "*Does not turn around.*\n\n"
        "'Bring another candle. Then you may go.'"
    ),
}

# ─────────────────────────────────────
# 커스텀 CSS
# ─────────────────────────────────────
CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=IM+Fell+English:ital@0;1&display=swap');

.stApp {{
    background-color: #0d0a0e;
}}

.main .block-container {{
    max-width: 780px;
    padding-top: 0;
}}

/* 채팅 헤더 이미지 */
.queen-header {{
    width: 100%;
    max-height: 220px;
    object-fit: cover;
    object-position: top;
    display: block;
    border-bottom: 1px solid #3a2d1e;
    margin-bottom: 0.5rem;
}}

/* 헤더 제목 영역 */
.header-title {{
    text-align: center;
    padding: 0.5rem 0 1rem;
    border-bottom: 1px solid #2a1e35;
    margin-bottom: 1rem;
}}

.header-title h1 {{
    font-family: 'Cinzel', serif;
    color: #c9a96e;
    letter-spacing: 0.15em;
    font-size: 1.6rem;
    text-shadow: 0 0 30px rgba(201,169,110,0.3);
    margin: 0.3rem 0 0.2rem;
}}

.header-title p {{
    font-family: 'IM Fell English', serif;
    color: #7a6a5a;
    font-style: italic;
    font-size: 0.8rem;
    margin: 0;
}}

/* 말풍선 공통 */
.stChatMessage {{
    background-color: transparent !important;
    border: none !important;
    padding: 0.3rem 0 !important;
}}

/* 왕비 말풍선 (왼쪽) */
.stChatMessage[data-testid="chat-message-assistant"] {{
    background-color: transparent !important;
}}

.stChatMessage[data-testid="chat-message-assistant"] .stMarkdown {{
    background-color: #1e1428 !important;
    border: 1px solid #4a2d7a !important;
    border-radius: 0 16px 16px 16px !important;
    padding: 0.9rem 1.1rem !important;
    max-width: 80% !important;
    display: inline-block !important;
}}

.stChatMessage[data-testid="chat-message-assistant"] p {{
    font-family: 'IM Fell English', serif;
    color: #d4c5b0 !important;
    font-size: 0.95rem;
    line-height: 1.9;
    margin: 0 !important;
}}

.stChatMessage[data-testid="chat-message-assistant"] em {{
    color: #7a6a9a !important;
    font-style: italic;
}}

/* 유저 말풍선 (오른쪽) */
.stChatMessage[data-testid="chat-message-user"] {{
    background-color: transparent !important;
    flex-direction: row-reverse !important;
}}

.stChatMessage[data-testid="chat-message-user"] .stMarkdown {{
    background-color: #2d1e3e !important;
    border: 1px solid #6b3fa0 !important;
    border-radius: 16px 0 16px 16px !important;
    padding: 0.8rem 1.1rem !important;
    max-width: 75% !important;
    display: inline-block !important;
    float: right !important;
}}

.stChatMessage[data-testid="chat-message-user"] p {{
    font-family: 'IM Fell English', serif;
    color: #c9a96e !important;
    font-size: 0.95rem;
    margin: 0 !important;
}}

/* 입력창 */
.stChatInputContainer {{
    border-top: 1px solid #2a1e35 !important;
    padding-top: 0.8rem !important;
    background-color: #0d0a0e !important;
}}

.stChatInputContainer textarea {{
    background-color: #1a1020 !important;
    color: #c9a96e !important;
    border: 1px solid #3a2d4a !important;
    border-radius: 4px !important;
    font-family: 'IM Fell English', serif !important;
    font-size: 0.95rem !important;
}}

.stChatInputContainer textarea::placeholder {{
    color: #4a3d5a !important;
    font-style: italic;
}}

/* 언어 선택 버튼 */
.stButton button {{
    background-color: rgba(30, 20, 40, 0.8) !important;
    color: #c9a96e !important;
    border: 1px solid #4a3d5a !important;
    font-family: 'Cinzel', serif !important;
    letter-spacing: 0.1em;
    transition: all 0.3s;
}}

.stButton button:hover {{
    background-color: rgba(60, 40, 80, 0.8) !important;
    border-color: #c9a96e !important;
}}

::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: #0d0a0e; }}
::-webkit-scrollbar-thumb {{ background: #3a2d4a; border-radius: 2px; }}
</style>
"""

# ─────────────────────────────────────
# Streamlit UI
# ─────────────────────────────────────
st.set_page_config(
    page_title="Queen's Chamber",
    page_icon="👑",
    layout="centered"
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────
# 언어 선택 화면
# ─────────────────────────────────────
if "lang" not in st.session_state:
    st.markdown(
        f'<img src="data:image/jpg;base64,{queen_main}" '
        f'style="width:100%; max-height:400px; object-fit:cover; '
        f'object-position:top; display:block; margin-bottom:2rem;">',
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align:center;'>"
        "<h1 style='font-family:Cinzel,serif; color:#c9a96e; "
        "letter-spacing:0.15em; font-size:2rem; "
        "text-shadow:0 0 30px rgba(201,169,110,0.3);'>"
        "👑 Queen's Chamber</h1>"
        "<p style='font-family:IM Fell English,serif; color:#7a6a5a; "
        "font-style:italic; font-size:0.9rem;'>"
        "She has no name. She was only ever the Queen.</p>"
        "<p style='font-family:IM Fell English,serif; color:#4a3d5a; "
        "font-style:italic; font-size:0.85rem; margin-top:2rem;'>"
        "Choose your language to enter her chamber.</p>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🇰🇷  한국어", use_container_width=True):
            st.session_state.lang = "ko"
            st.session_state.messages = [{"role": "assistant", "content": OPENING["ko"]}]
            st.rerun()
    with col2:
        if st.button("🇯🇵  日本語", use_container_width=True):
            st.session_state.lang = "ja"
            st.session_state.messages = [{"role": "assistant", "content": OPENING["ja"]}]
            st.rerun()
    with col3:
        if st.button("🇺🇸  English", use_container_width=True):
            st.session_state.lang = "en"
            st.session_state.messages = [{"role": "assistant", "content": OPENING["en"]}]
            st.rerun()
    st.stop()

# ─────────────────────────────────────
# 채팅 화면
# ─────────────────────────────────────
placeholder = {
    "ko": "왕비에게 말을 건네세요...",
    "ja": "王妃に話しかけてください...",
    "en": "Speak to the Queen...",
}

# 채팅 헤더 이미지
st.markdown(
    f'<img src="data:image/jpg;base64,{queen_chat}" class="queen-header">',
    unsafe_allow_html=True
)

# 제목
st.markdown(
    "<div class='header-title'>"
    "<h1>👑 Queen's Chamber</h1>"
    "<p>She has no name. She was only ever the Queen.</p>"
    "</div>",
    unsafe_allow_html=True
)

# 대화 기록 출력
for message in st.session_state.messages:
    icon = "👑" if message["role"] == "assistant" else "🕯️"
    with st.chat_message(message["role"], avatar=icon):
        st.markdown(message["content"])

# 유저 입력
if prompt := st.chat_input(placeholder[st.session_state.lang]):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🕯️"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="👑"):
        with st.spinner("..."):
            try:
                history = []
                for msg in st.session_state.messages[1:-1]:
                    role = "user" if msg["role"] == "user" else "model"
                    history.append({"role": role, "parts": [{"text": msg["content"]}]})

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=history + [{"role": "user", "parts": [{"text": prompt}]}],
                    config={
                        "system_instruction": SYSTEM_PROMPT,
                        "temperature": 0.9,
                    }
                )
                reply = response.text

            except Exception as e:
                reply = f"오류가 발생했습니다: {str(e)}"

            st.markdown(reply)
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })