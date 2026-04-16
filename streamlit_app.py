import streamlit as st
import requests

# ---------------------------
# CONFIG
# ---------------------------
API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="GenAI Language Coach", layout="wide")

# ---------------------------
# STYLING
# ---------------------------
st.markdown("""
<style>
.big-title {
    font-size: 40px;
    font-weight: bold;
}
.card {
    padding: 15px;
    border-radius: 12px;
    background-color: #f3f3f3;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# FLAG DETECTION
# ---------------------------
def detect_flag(user_input: str) -> str:
    text = (user_input or "").lower()
    if "spanish" in text:
        return "🇪🇸"
    elif "german" in text:
        return "🇩🇪"
    elif "russian" in text:
        return "🇷🇺"
    elif "french" in text:
        return "🇫🇷"
    elif "italian" in text:
        return "🇮🇹"
    else:
        return "🌍"

# ---------------------------
# SAFE PHRASE RENDERER (FIX)
# ---------------------------
def render_phrase_card(phrase: dict, flag: str):
    """
    Renders a phrase safely (no fragile big HTML blocks).
    Prevents empty white cards by using .get() with fallbacks.
    """
    st.markdown('<div class="card">', unsafe_allow_html=True)

    sentence = phrase.get("sentence", "")
    english = phrase.get("english_translation", "")
    native = phrase.get("native_translation", "")
    ipa = phrase.get("ipa", "")

    # Title
    if sentence:
        st.markdown(f"### {flag} {sentence}")
    else:
        st.markdown(f"### {flag} (No sentence returned)")

    # English
    if english:
        st.write("🇬🇧 English:", english)
    else:
        st.write("🇬🇧 English: N/A")

    # Native (only if present and not duplicate)
    if native and native != english:
        st.write("🗣 Native:", native)

    # IPA
    if ipa:
        st.write("🔊 IPA:", ipa)

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------
# LAYOUT (MAIN + IPA PANEL)
# ---------------------------
col1, col2 = st.columns([3, 1])

# ===========================
# MAIN APP (LEFT)
# ===========================
with col1:

    st.markdown("<div class='big-title'>🌍 GenAI Language Coach</div>", unsafe_allow_html=True)
    st.write("Practice languages using text or speech.")

    # ---------------------------
    # TEXT INPUT
    # ---------------------------
    st.markdown("---")
    st.subheader("✍️ Type your request")

    user_input = st.text_input(
        "",
        placeholder="I want to practice Spanish. My native language is English."
    )

    flag = detect_flag(user_input)

    if user_input and st.session_state.get("last_input") != user_input:
        st.session_state["last_input"] = user_input

        try:
            response = requests.post(
                f"{API_BASE}/agent/natural",
                json={"message": user_input}
            )

            if response.status_code == 200:
                data = response.json()
                st.success("Response received!")

                if "data" in data and "phrases" in data["data"]:
                    for phrase in data["data"]["phrases"]:
                        render_phrase_card(phrase, flag)
                else:
                    st.write(data)

            else:
                st.error(response.text)

        except Exception as e:
            st.error(f"Error: {e}")

    # ---------------------------
    # SPEECH INPUT
    # ---------------------------
    st.markdown("---")
    st.subheader("🎤 Upload Speech")

    speech_file = st.file_uploader("Upload a .wav file", type=["wav"], key="speech")

    if speech_file:
        st.audio(speech_file)

        try:
            response = requests.post(
                f"{API_BASE}/agent/speech",
                files={"file": speech_file}
            )

            if response.status_code == 200:
                data = response.json()
                st.success("Speech processed!")

                if "data" in data and "phrases" in data["data"]:
                    for phrase in data["data"]["phrases"]:
                        render_phrase_card(phrase, flag)
                else:
                    st.write(data)

            else:
                st.error(response.text)

        except Exception as e:
            st.error(f"Error: {e}")

    # ---------------------------
# PRONUNCIATION SCORING (FINAL)
# ---------------------------
st.markdown("---")
st.subheader("🎯 Pronunciation Scoring")

ref_audio = st.file_uploader("Reference audio (.wav)", type=["wav"], key="ref")
user_audio = st.file_uploader("Your audio (.wav)", type=["wav"], key="user")

if ref_audio:
    st.audio(ref_audio)
if user_audio:
    st.audio(user_audio)

if st.button("Score Pronunciation"):

    if not ref_audio or not user_audio:
        st.warning("Please upload BOTH audio files.")
    else:
        try:
            with st.spinner("Analyzing pronunciation..."):

                files = {
                    "reference": ("reference.wav", ref_audio, "audio/wav"),
                    "user": ("user.wav", user_audio, "audio/wav")
                }

                response = requests.post(
                    f"{API_BASE}/pronunciation/score",
                    files=files
                )

                if response.status_code != 200:
                    st.error(response.text)
                else:
                    result = response.json()

                    score = result.get("score", 0)
                    similarity = result.get("similarity", 0)

                    # 🎯 VISUAL SCORE
                    st.markdown(
                        f"<h1 style='color:#8A2BE2; text-align:center;'>Score: {score}/5</h1>",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"<p style='text-align:center;'>Similarity: {similarity:.2f}</p>",
                        unsafe_allow_html=True
                    )

                    # 🎯 INTERPRETATION (better)
                    if score >= 4.2:
                        st.success("Near-native pronunciation")
                    elif score >= 3.5:
                        st.success("Strong pronunciation")
                    elif score >= 2.8:
                        st.warning("Understandable, needs refinement")
                    else:
                        st.error("Significant improvement needed")

        except Exception as e:
            st.error(f"Error processing audio: {e}")


# ===========================
# IPA PANEL (RIGHT) — UPGRADED
# ===========================
with col2:

    st.markdown("## 🔤 IPA Guide")

    st.markdown("### 🟣 Vowels")
    st.markdown("""
- **/i/** → *see*  
- **/ɪ/** → *sit*  
- **/e/** → *bed*  
- **/æ/** → *cat*  
- **/ɑ/** → *father*  
- **/ɔ/** → *thought*  
- **/o/** → *go*  
- **/u/** → *food*  
""")

    st.markdown("### 🔵 Consonants")
    st.markdown("""
- **/ʃ/** → *she*  
- **/tʃ/** → *chair*  
- **/ʒ/** → *measure*  
- **/θ/** → *think*  
- **/ð/** → *this*  
- **/r/** → rolled/soft r  
""")

    st.markdown("### 🟢 Stress & Length")
    st.markdown("""
- **ˈword** → primary stress  
- **ː** → long vowel  
""")

    st.markdown("### 💡 Quick Tips")
    st.markdown("""
- IPA ≠ spelling  
- Focus on **sounds**, not letters  
- Stress placement changes meaning  
""")

    st.caption("Quick pronunciation reference for learners")