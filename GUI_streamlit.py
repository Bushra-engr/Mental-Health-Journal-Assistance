import streamlit as st
import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
from datetime import datetime

# 🎨 Page configuration
st.set_page_config(
    page_title="AI Mental Health Journal Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎭 Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .journal-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .response-container {
        background-color: #e8f4fd;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    .emotion-badge {
        display: inline-block;
        padding: 5px 15px;
        background-color: #667eea;
        color: white;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# 🔧 Initialize session state
if 'journal_history' not in st.session_state:
    st.session_state.journal_history = []

def load_api_key():
    """Load API key from environment or user input"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.sidebar.warning("⚠️ Gemini API key not found in environment variables")
        api_key = st.sidebar.text_input(
            "Enter your Gemini API Key:",
            type="password",
            help="Get your API key from Google AI Studio"
        )
    
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

def load_system_prompt():
    """Load system prompt from file or use default"""
    prompt_file = Path("prompts/sys_prompts.txt")
    
    try:
        if prompt_file.exists():
            with open(prompt_file, "r") as file:
                return file.read()
    except Exception as e:
        st.sidebar.error(f"Error loading prompt file: {e}")
    
    # Default system prompt
    return """You are a compassionate AI mental health journal assistant. Your role is to:
1. Analyze the emotional content of journal entries
2. Provide supportive, empathetic responses
3. Offer gentle guidance and mental health insights
4. Maintain a warm, understanding tone

Always respond in JSON format with:
- emotion_detected: main emotion identified
- summary: brief summary of the entry
- advice: supportive message or advice
- tone: empathetic and encouraging"""

def get_ai_response(user_input, system_prompt):
    """Get response from Gemini AI"""
    try:
        model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        
        combined_prompt = f"""{system_prompt}

User Journal Entry:
\"\"\"{user_input}\"\"\"

Respond with:
- Emotion detected
- Short summary
- Advice or mental health support message
- Tone: empathetic and warm

Format your response as valid JSON with keys: emotion_detected, summary, advice"""

        response = model.generate_content(
            combined_prompt,
            generation_config={"temperature": 0.9}
        )
        
        # Clean the response text
        raw_text = response.text
        clean_text = re.sub(r"```json|```", "", raw_text).strip()
        
        # Parse JSON
        try:
            response_json = json.loads(clean_text)
            return response_json, None
        except json.JSONDecodeError:
            return None, raw_text
            
    except Exception as e:
        return None, f"Error: {str(e)}"

# 🏠 Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">🧠 AI Mental Health Journal Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🔧 Settings")
    
    # API Key setup
    if not load_api_key():
        st.error("Please provide your Gemini API key to continue.")
        st.info("💡 You can get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
        return
    
    # Load system prompt
    system_prompt = load_system_prompt()
    
    # Sidebar options
    st.sidebar.subheader("📊 Session Info")
    st.sidebar.info(f"Entries today: {len(st.session_state.journal_history)}")
    
    if st.sidebar.button("🗑️ Clear History"):
        st.session_state.journal_history = []
        st.rerun()
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Your Journal Entry")
        
        # Journal input
        user_input = st.text_area(
            "How are you feeling today? Share your thoughts:",
            height=200,
            placeholder="Express your thoughts, emotions, or experiences here..."
        )
        
        # Buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            analyze_btn = st.button("🔍 Analyze Entry", type="primary", use_container_width=True)
        
        with col_btn2:
            if st.button("💾 Save Entry", use_container_width=True):
                if user_input.strip():
                    entry = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "entry": user_input,
                        "analysis": None
                    }
                    st.session_state.journal_history.append(entry)
                    st.success("Entry saved!")
                else:
                    st.warning("Please write something before saving.")
    
    with col2:
        st.subheader("🤖 AI Analysis")
        
        if analyze_btn and user_input.strip():
            with st.spinner("🧠 Analyzing your entry..."):
                response_json, error = get_ai_response(user_input, system_prompt)
                
                if response_json:
                    st.markdown('<div class="response-container">', unsafe_allow_html=True)
                    
                    # Display emotion
                    if "emotion_detected" in response_json:
                        st.markdown(f'<div class="emotion-badge">😊 Emotion: {response_json["emotion_detected"]}</div>', unsafe_allow_html=True)
                    
                    # Display summary
                    if "summary" in response_json:
                        st.markdown("**📋 Summary:**")
                        st.write(response_json["summary"])
                    
                    # Display advice
                    if "advice" in response_json:
                        st.markdown("**💡 AI Guidance:**")
                        st.write(response_json["advice"])
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Save analysis to history
                    entry = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "entry": user_input,
                        "analysis": response_json
                    }
                    st.session_state.journal_history.append(entry)
                    
                else:
                    st.error("⚠️ Unexpected response format")
                    with st.expander("View raw response"):
                        st.text(error)
        
        elif analyze_btn:
            st.warning("Please write something in your journal entry first.")
    
    # Journal History
    if st.session_state.journal_history:
        st.markdown("---")
        st.subheader("📚 Journal History")
        
        for i, entry in enumerate(reversed(st.session_state.journal_history)):
            with st.expander(f"📅 Entry {len(st.session_state.journal_history)-i} - {entry['timestamp']}"):
                st.markdown('<div class="journal-container">', unsafe_allow_html=True)
                st.markdown("**Your Entry:**")
                st.write(entry['entry'])
                
                if entry['analysis']:
                    st.markdown("**AI Analysis:**")
                    if "emotion_detected" in entry['analysis']:
                        st.markdown(f"🎭 **Emotion:** {entry['analysis']['emotion_detected']}")
                    if "summary" in entry['analysis']:
                        st.markdown(f"📋 **Summary:** {entry['analysis']['summary']}")
                    if "advice" in entry['analysis']:
                        st.markdown(f"💡 **Advice:** {entry['analysis']['advice']}")
                
                st.markdown('</div>', unsafe_allow_html=True)

# 🚀 Run the app
if __name__ == "__main__":
    main()
