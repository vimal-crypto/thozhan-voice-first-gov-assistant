import os
import json
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = "REMOVED_KEY"


class AgenticCrawler:
    def __init__(self):
        self.ddgs = DDGS()
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    def search_and_scrape(self, query: str):
        print(f"Crawler searching for: {query}")
        
        try:
            results = list(self.ddgs.text(f"{query} tamil nadu government scheme eligibility", max_results=3))
        except Exception as e:
            print(f"Search failed: {e}")
            return None

        if not results:
            return None

        raw_text = ""
        for res in results:
            url = res['href']
            print(f"   -> Scraping: {url}")
            try:
                page = requests.get(url, timeout=5)
                soup = BeautifulSoup(page.content, 'html.parser')
                text = " ".join([p.text for p in soup.find_all(['p', 'h1', 'h2', 'h3'])])
                raw_text += f"\nSOURCE: {url}\nCONTENT: {text[:2000]}\n"
            except Exception as e:
                print(f"      Failed to scrape {url}: {e}")

        if not raw_text:
            return None

        print("[AI] Groq/Llama is structuring data...")
        prompt = f"""
        You are an AI Helper for Tamil Nadu schemes.
        Extract the scheme details from the text below into strictly valid JSON.
        Information needed: Name, Description, Eligibility (List), Benefits.
        Translate content to Tamil where requested.

        Raw Text:
        {raw_text}

        Target JSON Schema:
        {{
            "name_english": "Name",
            "name_tamil": "Tamil Name",
            "description_english": "1-2 sentence description",
            "description_tamil": "1-2 sentence description in Tamil",
            "eligibility_criteria": ["Criteria 1", "Criteria 2"],
            "benefits_english": "Benefits",
            "benefits_tamil": "Benefits in Tamil",
            "category": "New"
        }}

        Return ONLY the JSON object. If no scheme found, return {{ "error": "not_found" }}.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            cleaned = response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)
            
            if "error" in data:
                return None
            
            self._save_to_db(data)
            return data
            
        except Exception as e:
            print(f"[ERROR] Groq Extraction failed: {e}")
            return None

    def _save_to_db(self, new_scheme):
        db_path = os.path.join("voice_agent", "data", "schemes_tamil.json")
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            
            db.append(new_scheme)
            
            with open(db_path, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
            print("[DB] New scheme saved to Database!")
        except Exception as e:
            pass
