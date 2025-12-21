# Thozhan (தோழன்) - AI-Powered Voice Assistant for Government Schemes
Thozhan is a **voice-first, vernacular-native assistant** that helps Tamil-speaking citizens discover and access government welfare schemes without needing to read, type, or navigate complex portals. It is designed as a reliable, contextual, and human-like guide rather than just another chatbot.

---

## Why Thozhan is Different

### 1. Solving the Real Access Barrier

Most government portals assume that users can comfortably **read, type, and navigate UI in English or formal Tamil**. Thozhan flips this assumption by being:

- **Voice-first**: Users can speak naturally instead of typing.
- **Vernacular-native**: Tamil is treated as the *primary interface*, not a translated layer.
- **Accessibility-focused**: Designed for users who are illiterate, tech-shy, or using shared/low-end devices.

The goal is simple: if a citizen is **eligible** for a benefit, lack of digital literacy should never be the reason they miss it.

---

### 2. Hybrid Agentic Architecture

Standard LLM chatbots often hallucinate, which is unacceptable when dealing with **financial welfare and eligibility**. Thozhan uses a **hybrid tool architecture** to balance reliability and coverage:

- **Verified Local Knowledge Base (Primary)**  
  - Curated database of major central and state schemes, eligibility rules, benefit amounts, and required documents.  
  - Used as the first source of truth for answering questions.  
  - Ensures **near 100% accuracy** on high-impact, frequently used schemes.

- **Live Web Crawler (Fallback / Secondary)**  
  - Activated only for niche, long-tail, or recently updated schemes not present in the local store.  
  - Used in a controlled way to reduce hallucinations.  
  - Responses are clearly framed when external sources are involved.

This hybrid approach keeps the assistant **trustworthy, auditable, and safe** for real-world usage.

---

### 3. Contextual Intelligence

Thozhan is built to behave like a **helpful, memory-aware guide**, not a stateless FAQ bot.

- Maintains **conversational memory** across turns.
- Remembers key user attributes shared in the session, such as:
  - Occupation (e.g., farmer, student, daily wage worker)
  - Location (district/state)
  - Economic background (e.g., below poverty line)
- Uses this context to:
  - Filter and prioritize more relevant schemes.
  - Personalize follow-up questions.
  - Avoid repeating already collected information.

**Example:**  
If the user mentions early in the conversation, *"I am a small farmer from Dindigul"*, Thozhan will remember this and, five turns later, automatically highlight farmer-specific loan waivers, subsidies, or insurance schemes instead of generic suggestions.

---

## High-Level Architecture

At a conceptual level, Thozhan consists of:

- **Voice & Interface Layer**
  - Speech-to-Text (Tamil)
  - Text-to-Speech (natural Tamil voice)
  - Simple mobile-friendly UI

- **Orchestration & Agent Layer**
  - Conversation manager with memory
  - Tool/router that decides when to:
    - Query local scheme database
    - Trigger web crawler
    - Ask clarification questions

- **Knowledge & Data Layer**
  - Structured scheme database (central + state schemes)
  - Metadata for eligibility rules, documents, deadlines, and links
  - Logging for auditability and improvements

---

## Demo Scenario (For Reviewers)

This repository is primarily for **project demo submission**. A typical demo flow looks like this:

1. User taps the mic and speaks in Tamil:  
   "நான் ஒரு சிறு விவசாயி. என்னக்கு என்னென்ன அரசு உதவித் திட்டங்கள் கிடைக்கும்?"

2. Thozhan:
   - Converts speech to text.
   - Detects that the user is a **farmer**.
   - Queries the **local scheme database** for farmer-related schemes.
   - Responds in spoken Tamil with:
     - Relevant schemes.
     - Eligibility summary.
     - Next steps (e.g., where to apply, what documents are needed).

3. If the user asks about a very new or niche scheme:
   - The assistant switches to the **web crawler**.
   - Fetches and summarizes updated information.
   - Clearly indicates that it is using an external source.

---

## Repository Structure (Planned)

This repo is currently focused on explaining the concept and architecture for demo purposes. Planned structure:

- `README.md` – Concept, architecture, and demo explanation (this file)
- `architecture/` – Diagrams and design notes (to be added)
- `data/` – Sample scheme metadata / mock database (to be added)
- `notebooks/` – Prototype experiments for STT, TTS, and intent classification (to be added)
- `app/` – Backend / orchestration code (to be added)
- `ui/` – Frontend or mobile interface (to be added)

---

## Status

- ✅ Concept and system design finalized  
- ✅ Demo-ready narrative for evaluation  
- 🔄 Implementation and code cleanup in progress  
- 🔜 Will be updated with code, data samples, and architecture diagrams after demo submission

---

## How to Use This Repo for the Demo

- Treat this repository as the **official reference** for:
  - Problem framing
  - Core differentiators
  - Architecture philosophy
  - Example interaction flow
- Post-demo, this repo will evolve into a **full implementation** with:
  - Deployed prototype
  - API endpoints
  - Sample configuration for different states / languages

---

## Contact

For collaboration, feedback, or implementation discussions, please reach out via GitHub profile.

---

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- Microphone access (for voice input)
- Active internet connection

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/vimal-crypto/thozhan-voice-first-gov-assistant.git
cd thozhan-voice-first-gov-assistant
```

#### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set Up API Keys

**Get your FREE Groq API Key:**
1. Visit [https://console.groq.com/](https://console.groq.com/)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key

**Configure Environment Variables:**

Create a `.env` file in the project root:

```bash
# .env
GROQ_API_KEY=your_groq_api_key_here
```

**Alternative:** Export directly in terminal:

```bash
# Windows
set GROQ_API_KEY=your_groq_api_key_here

# macOS/Linux
export GROQ_API_KEY=your_groq_api_key_here
```

#### 5. Create Project Structure

Create the following folders:

```bash
mkdir -p voiceagent/data voiceagent/temp_audio static
```

---

## 📁 Project Structure

```
thozhan-voice-first-gov-assistant/
├── app.py                          # FastAPI server & main application
├── voiceagent/
│   ├── __init__.py                # Package initializer
│   ├── agent.py                    # LangGraph agent with tools
│   ├── audio_utils.py              # STT & TTS handlers
│   ├── crawler_tool.py             # Web scraping tool
│   ├── data/
│   │   └── schemes_tamil.json      # Local scheme database
│   └── temp_audio/                 # Temporary audio files
├── static/
│   └── index.html                  # Web UI
├── requirements.txt                # Python dependencies
├── .env                            # API keys (create this)
├── .gitignore
├── LICENSE
└── README.md
```

---

## ▶️ Running the Application

### Start the Server

```bash
python app.py
```

The server will start on `http://localhost:8000`

### Access the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

---

## 🎯 How to Use

1. **Grant Microphone Permission** when prompted by your browser
2. **Click the Microphone Button** at the bottom of the screen
3. **Speak in Tamil** about the government scheme you're looking for
   - Example: "நான் ஒரு விவசாயி. எனக்கு கடன் உதவி தேவை"
4. **Wait for Response** - Thozhan will:
   - Convert your speech to text
   - Search the local database first
   - Fall back to web search if needed
   - Respond with scheme details in Tamil (both text and voice)

---

## 🔧 Configuration

### Modifying System Prompt

Edit `voiceagent/agent.py` to customize the AI behavior:

```python
SYSTEM_PROMPT = """
Your custom instructions here...
"""
```

### Adding Schemes to Database

Edit `voiceagent/data/schemes_tamil.json` to add verified schemes:

```json
[
  {
    "name_english": "PM Kisan",
    "name_tamil": "பிரதமர் கிசான்",
    "description_english": "Direct income support",
    "description_tamil": "நேரடி வருமான உதவி",
    "eligibility_criteria": ["Small farmers", "Own land"],
    "benefits_english": "₹6000 per year",
    "benefits_tamil": "ஆண்டுக்கு ₹6000",
    "category": "Agriculture"
  }
]
```

---

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution:** Make sure you've set the environment variable or created a `.env` file

### Issue: "No module named 'voiceagent'"
**Solution:** Make sure you're in the project root directory and the `voiceagent` folder exists

### Issue: "Microphone not working"
**Solution:** 
- Check browser permissions
- Use HTTPS or localhost (required for mic access)
- Try a different browser

### Issue: "FFmpeg not found"
**Solution:**
```bash
pip install static-ffmpeg
```

---

## 📝 Code Files Overview

### `app.py`
Main FastAPI application that:
- Serves the web interface
- Handles audio file uploads
- Coordinates STT → Agent → TTS pipeline
- Manages conversation history

### `voiceagent/agent.py`
LangGraph agentic system with:
- Local database search tool
- Web crawler fallback tool
- Groq LLM (Llama 3.3 70B)
- Conditional routing logic

### `voiceagent/audio_utils.py`
Audio processing utilities:
- Speech-to-Text (Google Speech Recognition)
- Text-to-Speech (Edge TTS with Tamil voice)
- Audio format conversion

### `voiceagent/crawler_tool.py`
Web scraping tool that:
- Searches DuckDuckGo for schemes
- Scrapes government websites
- Extracts structured data using Groq LLM
- Saves new schemes to database

### `static/index.html`
Web UI with:
- Gemini-inspired dark theme
- Voice recording functionality
- Real-time audio playback
- Chat interface

---

## 🌟 Features Implemented

✅ Voice-first Tamil interface  
✅ Speech-to-Text (Tamil)  
✅ Text-to-Speech (Tamil)  
✅ Hybrid tool architecture (Local DB + Web Crawler)  
✅ LangGraph agentic system  
✅ Conversational memory  
✅ Web-based UI  
✅ Real-time audio processing  

---

## 📦 Dependencies Explained

- **FastAPI**: Modern web framework for the API
- **LangChain & LangGraph**: Agentic AI orchestration
- **Groq**: Fast LLM inference (free tier available)
- **SpeechRecognition**: Speech-to-text
- **Edge-TTS**: Natural Tamil text-to-speech
- **BeautifulSoup4**: Web scraping
- **DuckDuckGo-Search**: Privacy-focused search

---

## 🔐 Security Notes

- **Never commit `.env` file** - it contains your API keys
- **API keys are free** - Groq offers generous free tier
- **Local processing** - STT/TTS happens on your machine
- **No data storage** - Conversation history is in-memory only

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📧 Support

For issues or questions:
- Open a GitHub Issue
- Check existing issues first
- Provide error logs and system info

---

**Built with ❤️ for Tamil-speaking citizens seeking government welfare assistance**

For collaboration, feedback, or implementation discussions, please reach out via GitHub profile.
