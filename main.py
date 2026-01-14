import os
import google.generativeai as genai
import requests
from datetime import datetime
from duckduckgo_search import DDGS

# --- CONFIGURATION ---

# PASTE YOUR GEM INSTRUCTIONS HERE
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

def get_search_results(query):
    """Searches the web using DuckDuckGo (Free)"""
    print(f"Searching for: {query}")
    try:
        results = DDGS().text(query, max_results=5)
        # Combine the snippets into one block of text
        context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
        return context
    except Exception as e:
        print(f"Search error: {e}")
        return "No search results found."

def run_bot():
    # 1. Setup Gemini
    api_key = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # We use the standard stable model (no experimental/beta tools)
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash', 
        system_instruction=GEM_INSTRUCTIONS
    )
    
    # 2. Get Data (The "Manual" Search)
    today = datetime.now().strftime("%Y-%m-%d")
    search_query = f"MLB and NBA betting odds and player news for today {today}"
    
    # Perform the search FIRST
    search_context = get_search_results(search_query)
    
    # 3. Ask Gemini (Feeding it the search data)
    prompt = f"""
    Today is {today}.
    Here is the latest news and odds I found on the web:
    
    {search_context}
    
    Based on this information, please generate my daily betting report.
    """
    
    print("Asking Gemini to analyze the search results...")
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text
    except Exception as e:
        analysis = f"Error generating analysis: {str(e)}"
        print(analysis)

    # 4. Send to Discord
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    # Discord has a 2000 character limit per message, so we split if needed
    if len(analysis) > 1900:
        analysis = analysis[:1900] + "\n...(message truncated due to length)"

    payload = {
        "content": f"## 🎲 Daily Betting Report for {today}\n{analysis}"
    }
    
    print("Sending to Discord...")
    requests.post(webhook_url, json=payload)
    print("Done!")

if __name__ == "__main__":
    run_bot()
