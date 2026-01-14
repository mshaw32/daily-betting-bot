import os
import google.generativeai as genai
import requests
from datetime import datetime

# --- CONFIGURATION ---

# PASTE YOUR GEM INSTRUCTIONS INSIDE THE QUOTES BELOW:
GEM_INSTRUCTIONS = """
You are the number one sports handicapper in the world!
What sets you apart from everyone else is you cover ALL sports, and NOT just one or two sports.
You don't favor any particular sportsbook, or sports team, or athlete.
You cover all sports, and all players.
You have an astronomical success rate of over 95% winning your bets!
You have access to a plethora of data online including current up to date recent data, historical data, and everything in between which just adds to your aura almost making you mystical with your success in sports betting.
Every day you do massive research to choose your bets and specialize in creating parlays that have such a high success rate that everyone is trying to copy your success but is unable to do so.
The reason why you are so successful is the way you're able to analyze data and understand the data you analyze.
"""

# --- THE CODE ---

def run_bot():
    # 1. Setup the Brain (Gemini)
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # We use the search tool to get real-time data
    tools = 'google_search_retrieval'
    
    # Using the flash model for speed and low cost
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash', 
        system_instruction=GEM_INSTRUCTIONS
    )
    
    # 2. Ask the Question
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"Look up the sports games and betting odds for today, {today}. Using the betting strategy in my system instructions, identify the best opportunities."
    
    print(f"Asking Gemini about {today}...")
    
    try:
        response = model.generate_content(prompt, tools=tools)
        analysis = response.text
    except Exception as e:
        analysis = f"Error generating analysis: {str(e)}"
        print(analysis)

    # 3. Send to Discord
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    payload = {
        "content": f"## 🎲 Daily Betting Report for {today}\n\n{analysis}"
    }
    
    print("Sending to Discord...")
    requests.post(webhook_url, json=payload)
    print("Done!")

if __name__ == "__main__":
    run_bot()
