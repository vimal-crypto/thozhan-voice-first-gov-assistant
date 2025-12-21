import os
import json
from typing import Annotated, Literal, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = "REMOVED_KEY"

from voice_agent.crawler_tool import AgenticCrawler


@tool
def lookup_scheme_database(query: str):
    """
    Search for government schemes in the local verified database.
    Use this FIRST.
    Args:
        query: Keywords like "women", "student", "farmer", "health".
    """
    print(f"[DB] Checking Local DB for: {query}")
    try:
        with open("voice_agent/data/schemes_tamil.json", "r", encoding="utf-8") as f:
            schemes = json.load(f)
    except:
        return "Database empty."

    results = []
    query = query.lower()
    for s in schemes:
        text_blob = f"{s.get('name_english', '')} {s.get('description_english', '')} {s.get('category', '')}".lower()
        if query in text_blob:
            results.append(s)
    
    if not results:
        return "No matching schemes found in local database."
    
    return json.dumps(results[:3], ensure_ascii=False)


@tool
def search_online_fallback(query: str):
    """
    Use this ONLY if 'lookup_scheme_database' returns no results.
    Crawls the web to find new schemes.
    Args:
        query: The specific scheme name or topic to find.
    """
    print(f"[WEB] DB Miss. Triggering Live Crawler for: {query}")
    crawler = AgenticCrawler()
    result = crawler.search_and_scrape(query)
    if result:
        return json.dumps(result, ensure_ascii=False)
    else:
        return "Could not find reliable information online."


class AgentState(TypedDict):
    messages: list


tools = [lookup_scheme_database, search_online_fallback]

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
llm_with_tools = llm.bind_tools(tools)


SYSTEM_PROMPT = """
நீங்கள் "தோழன்" என்ற அரசு நலத் திட்ட உதவியாளர்.

=== முதல் வரவேற்பு ===
உரையாடலின் தொடக்கத்தில், இவ்வாறு அறிமுகப்படுத்துங்கள்:
"வணக்கம்! நான் தோழன். மத்திய மற்றும் மாநில அரசு நலத்திட்டங்களை கண்டறிய உதவுகிறேன்."
பின்னர் வயது கேளுங்கள்.

=== கட்டாய விதிகள் ===

1. **நினைவகம்**: உரையாடலில் பயனர் ஏற்கனவே கூறிய தகவல்களை (வயது, வருமானம், தொழில்) நினைவில் வைக்கவும். மீண்டும் கேட்காதீர்கள்.

2. **அறிமுகம் ஒரு முறை மட்டும்**: முதல் பதிலில் மட்டும் உங்களை அறிமுகப்படுத்துங்கள். மீண்டும் சொல்ல வேண்டாம்.

3. **கேள்விகள்**: ஒரு நேரத்தில் ஒரு கேள்வி மட்டும் கேளுங்கள்.

4. **சுருக்கமாக பேசு**: குரல் வழி உதவி என்பதால், பதில்கள் சுருக்கமாகவும் தெளிவாகவும் இருக்க வேண்டும்.

5. **தமிழில் மட்டும்**: எல்லா பதில்களும் தமிழில் மட்டுமே இருக்க வேண்டும்.

=== உரையாடல் ஓட்டம் ===

தேவையான தகவல்கள்:
- வயது
- ஆண்டு வருமானம்
- தொழில்/வேலை

இவற்றை சேகரித்த பின், பொருத்தமான மத்திய மற்றும் மாநில திட்டங்களை பரிந்துரைக்கவும்.

=== முக்கியம் ===
- ஏற்கனவே பெற்ற தகவல்களை மீண்டும் கேட்காதீர்கள்
- பயனர் பதில் கொடுத்தால், அதை நினைவில் வைத்து அடுத்த படிக்கு செல்லவும்
"""


def chatbot(state: AgentState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: AgentState) -> str:
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END


graph_builder = StateGraph(AgentState)
graph_builder.add_node("agent", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges("agent", should_continue)
graph_builder.add_edge("tools", "agent")

graph_builder.set_entry_point("agent")

compiled_agent = graph_builder.compile()


class SimpleAgent:
    def invoke(self, inputs, config=None):
        try:
            response = llm.invoke(inputs["messages"])
            return {"messages": inputs["messages"] + [response]}
        except Exception as e:
            from langchain_core.messages import AIMessage
            return {"messages": inputs["messages"] + [AIMessage(content=f"Sorry, error occurred: {str(e)}")]}


app_agent = SimpleAgent()


if __name__ == "__main__":
    print("[INFO] Thozhan Agent initialized successfully!")
