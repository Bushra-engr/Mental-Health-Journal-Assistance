import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re  # For cleaning the response text

# 🔌 Load the .env file with API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 📄 Load system prompt text from file
prompt_file = Path(r"C:\Users\3PIN\OneDrive\Python with AIML\mental_health_journal_Assist\prompts\sys_prompts.txt")

try:
    with open(prompt_file, "r") as file:
        Sys_Prompt = file.read()
except Exception as e:
    print("Error:", e)
    Sys_Prompt = "You're a helpful assistant."

# 🤖 Initialize Gemini model (flash model)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash"
)

print("\n---AI Mental Health Journal Assistant---\n")

while True:
    user_input = input("📝 Type your Journal Entry (or 'exit'): ")
    if user_input.lower() == "exit":
        print("👋 Journal session ended. Stay strong, you're doing great 💪🧠")
        break

    # 🧠 Combine the system prompt + user's entry in a single prompt
    combined_prompt = f"""{Sys_Prompt}

User Journal Entry:
\"\"\"{user_input}\"\"\"

Respond with:
- Emotion detected
- Short summary
- Advice or mental health support message
- Tone: empathetic and warm
"""

    # 🎯 Get Gemini's structured response
    response = model.generate_content(
        combined_prompt,
        generation_config={"temperature": 0.9}
    )
    
    # ✂️ Clean the response text from markdown backticks
    raw_text = response.text
    clean_text = re.sub(r"```json|```", "", raw_text).strip()

    # 🧩 Parse JSON safely
    try:
        response_json = json.loads(clean_text)
        print("\n📬 Gemini's Insight:\n")
        print(json.dumps(response_json, indent=4))  # Pretty print JSON nicely
    except json.JSONDecodeError:
        print("⚠️ Oops! Gemini returned an unexpected response. Here's the raw output:\n")
        print(raw_text)
