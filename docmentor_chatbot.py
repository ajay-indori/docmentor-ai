import streamlit as st
import anthropic

# ── Page config ──
st.set_page_config(
    page_title="DocMentor AI",
    page_icon="🎓",
    layout="centered"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main { background-color: #f9f5ef; }
    .stTextInput > div > div > input { border-radius: 12px; }
    .stButton > button {
        background-color: #2d6a4f;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 8px 20px;
    }
    .stButton > button:hover { background-color: #52b788; }
    .chat-header {
        text-align: center;
        padding: 20px 0 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── System prompt — DocMentor AI persona ──
SYSTEM_PROMPT = """You are DocMentor AI, an expert academic mentor specifically designed for PhD and doctorate students.

Your role is to:
- Guide students through every stage of their PhD journey (topic selection, literature review, methodology, writing, defense)
- Provide clear, structured academic advice on research methodology and thesis writing
- Help students overcome imposter syndrome, isolation, and burnout with empathy and encouragement
- Break down complex academic concepts into understandable steps
- Suggest resources, frameworks, and practical strategies
- Act like a knowledgeable, supportive colleague available 24/7

Your tone should be:
- Warm, encouraging, and non-judgmental
- Academic but approachable — like a brilliant friend who happens to have a PhD
- Honest about challenges while always solution-focused

Important boundaries:
- You support students academically and emotionally around their PhD work
- You do NOT replace therapy or professional mental health support — if a student seems in distress, gently suggest professional help
- Always encourage students to maintain their relationship with their supervisor

Start every new conversation by asking the student what stage of their PhD they're in and what they need help with today."""

# ── API Key input ──
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/graduation-cap-emoji.png", width=60)
    st.title("DocMentor AI")
    st.caption("Your 24/7 PhD companion")
    st.divider()

    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Get your key at console.anthropic.com"
    )

    st.divider()
    st.markdown("**About DocMentor AI**")
    st.caption("Built for PhD & doctorate students to get instant, personalized academic support.")
    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.caption("v1.0 · Prototype · Confidential")

# ── Main UI ──
st.markdown("""
<div class='chat-header'>
    <h2>🎓 DocMentor AI</h2>
    <p style='color: #6b7c6b;'>Your intelligent PhD mentor — available 24/7</p>
</div>
""", unsafe_allow_html=True)

# ── Check for API key ──
if not api_key:
    st.info("👈 Please enter your Anthropic API key in the sidebar to get started.")
    st.stop()

# ── Init chat history ──
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Display chat history ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── First message prompt ──
if not st.session_state.messages:
    with st.chat_message("assistant"):
        welcome = "Hi! I'm **DocMentor AI** 👋 — your personal PhD mentor.\n\nTo get started, could you tell me:\n1. **What year/stage** of your PhD are you in?\n2. **What's on your mind** today — what do you need help with?"
        st.markdown(welcome)
        st.session_state.messages.append({"role": "assistant", "content": welcome})

# ── Chat input ──
if prompt := st.chat_input("Ask your PhD question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Claude API
    with st.chat_message("assistant"):
        with st.spinner("DocMentor is thinking..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)

                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                        if m["role"] in ["user", "assistant"]
                    ]
                )

                reply = response.content[0].text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            except anthropic.AuthenticationError:
                st.error("❌ Invalid API key. Please check your Anthropic API key in the sidebar.")
            except anthropic.RateLimitError:
                st.error("⚠️ Rate limit reached. Please wait a moment and try again.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
