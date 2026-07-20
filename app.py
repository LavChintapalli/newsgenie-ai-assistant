import streamlit as st
import os
import requests
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# =====================================================================
# 1. API KEY CONFIGURATION
# =====================================================================
os.environ["OPENAI_API_KEY"] = "openai-key-placeholder"
OPENAI_API_KEY = "openai-key-placeholder"
NEWS_API_KEY = "news-api-key-placeholder"
# =====================================================================
# 2. CORE FUNCTIONS
# =====================================================================
def fetch_live_news(search_keyword: str) -> list:
    """Fetches real-time articles using a direct search query instead of rigid categories."""
    # Using the /v2/everything endpoint means we can pass ANY word (like 'finance' or 'tech') directly!
    url = f"https://newsapi.org/v2/everything?q={search_keyword}&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            return articles[:3]
        return []
    except Exception:
        return []

def ai_agent_brain(user_input: str) -> str:
    """Intelligently routes traffic or searches for news dynamically."""
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY, temperature=0)
    
    system_prompt = (
        "You are the routing brain for NewsGenie.\n"
        "If the user is asking for recent news, headlines, or updates about a topic, "
        "reply with exactly: FETCH_NEWS: <topic> (replace <topic> with a single search keyword like finance, technology, or sports).\n"
        "Otherwise, if they are just chatting or asking general questions, reply with exactly: JUST_CHAT"
    )
    
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
    decision = llm.invoke(messages).content.strip()
    
    if "FETCH_NEWS" in decision:
        # Extract the search keyword the AI recommended
        try:
            search_keyword = decision.split(":")[-1].strip()
        except:
            search_keyword = "general"
            
        articles = fetch_live_news(search_keyword)
        if not articles:
            return f"I looked for recent news on '{search_keyword}', but couldn't find any articles right now."
        
        response = f"### 📰 Here are the latest updates for '{search_keyword}':\n\n"
        for art in articles:
            response += f"👉 **[{art.get('title')}]({art.get('url')})**\n*{art.get('description', 'No description available.')}*\n\n"
        return response
    else:
        chat_prompt = [
            SystemMessage(content="You are NewsGenie, a helpful AI assistant. Answer the user's query gracefully."),
            HumanMessage(content=user_input)
        ]
        return llm.invoke(chat_prompt).content

# =====================================================================
# 3. STREAMLIT CLEAN INTERFACE
# =====================================================================
st.set_page_config(page_title="NewsGenie Assistant", page_icon="🧞")

st.title("🧞 NewsGenie AI Assistant")
st.caption("Your intelligent portal for real-time news curation and general knowledge.")

# Simple input box—no sidebars, no dropdowns
user_query = st.text_input("Ask NewsGenie anything:")

if user_query:
    with st.spinner("🧞 Processing..."):
        answer = ai_agent_brain(user_query)
        st.write("---")
        st.write(answer)