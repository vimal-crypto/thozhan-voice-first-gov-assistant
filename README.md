# Thozhan (தோழன்) - Voice Assistant for Tamil Government Schemes

Thozhan helps Tamil-speaking people find government welfare schemes using voice - so they don't need to read or type anything. Built this because most govt portals are really hard to navigate, especially for people who aren't comfortable with English or typing.

## What Makes This Different

### 1. Voice-First in Tamil

Most government websites assume you can read and type in English or formal Tamil. But:
- People can just **speak naturally** in Tamil
- No need to know how to type or navigate menus
- Works for people who are not comfortable with tech

The idea is simple - if someone is eligible for a government benefit, they shouldn't miss it just because they can't use a computer well.

### 2. Hybrid Architecture (Local DB + Web Crawler)

I'm using two sources:

**Local Database (Primary)**
- Hand-curated list of major schemes
- Eligibility rules, benefit amounts, documents needed
- This ensures accuracy for important schemes
- No hallucinations!

**Web Crawler (Fallback)**
- Only used for new/niche schemes not in local DB
- Searches and scrapes govt websites
- Clearly indicates when using external source

This way it stays reliable but can still handle new schemes.

### 3. Contextual Memory

The assistant remembers what you said earlier in the conversation:
- Your occupation (farmer, student, daily worker, etc.)
- Your location (district/state)
- Your economic background

So if you mention "I'm a small farmer from Dindigul" early on, it'll remember and suggest relevant schemes automatically later.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                  (Voice + Web Interface)                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  VOICE & INTERFACE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  • Speech-to-Text (Tamil - Google Speech Recognition)           │
│  • Text-to-Speech (Tamil - Edge TTS)                            │
│  • Simple Mobile-Friendly UI                                    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              ORCHESTRATION & AGENT LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│  • Conversation Manager (Memory & Context)                      │
│  • LangGraph Agent (Groq - Llama 3.3 70B)                       │
│  • Tool Router & Decision Engine                                │
│                                                                 │
│   ┌────────────────────┐    ┌──────────────────────┐           │
│   │    Tool 1:         │    │    Tool 2:           │           │
│   │  Local DB Search   │    │   Web Crawler        │           │
│   │   (Primary)        │    │   (Fallback)         │           │
│   └────────────────────┘    └──────────────────────┘           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE & DATA LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  • Verified Scheme Database (schemes_tamil.json)                │
│  • Eligibility Rules & Criteria                                 │
│  • Document Requirements                                        │
│  • Application Links & Deadlines                                │
│  • Conversation Logs (In-Memory)                                │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                            │
├─────────────────────────────────────────────────────────────────┤
│  • DuckDuckGo Search API                                        │
│  • Government Websites (Tamil Nadu / Central)                   │
│  • Groq API (LLM Inference)                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Demo Flow

1. User speaks in Tamil: "நான் ஒரு சிறு விவசாயி. என்னக்கு என்னென்ன அரசு உதவித் திட்டங்கள் கிடைக்கும்?"
2. System converts speech → text → detects user is a farmer
3. Searches local database for farmer schemes
4. Responds with scheme details in Tamil (text + voice)
5. If asked about something not in DB, falls back to web search

## How to Run

### Prerequisites
- Python 3.8+
- FFmpeg (for audio)
- Microphone
- Internet connection

### Setup

```bash
git clone https://github.com/vimal-crypto/thozhan-voice-first-gov-assistant.git
cd thozhan-voice-first-gov-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Get FREE Groq API Key
# 1. Go to https://console.groq.com/
# 2. Sign up (it's free!)
# 3. Create API key

# Set up environment variable
export GROQ_API_KEY="your_api_key_here"  # On Windows: set GROQ_API_KEY=...

# Or create .env file:
echo "GROQ_API_KEY=your_api_key_here" > .env

# Run the app
python app.py
```

Open `http://localhost:8000` in your browser.

## Project Structure

```
thozhan-voice-first-gov-assistant/
├── app.py                    # Main FastAPI server
├── voiceagent/
│   ├── agent.py              # LangGraph agent with tools
│   ├── audio_utils.py        # STT & TTS handlers  
│   ├── crawler_tool.py       # Web scraping tool
│   ├── data/
│   │   └── schemes_tamil.json  # Local scheme database
│   └── temp_audio/           # Temp audio files
├── static/
│   └── index.html            # Web UI
├── requirements.txt
├── .env                      # Your API keys (DON'T COMMIT THIS!)
└── README.md
```

## Tech Stack

- **FastAPI** - Web framework
- **LangChain/LangGraph** - AI orchestration
- **Groq** - Fast LLM inference (free tier)
- **Google Speech Recognition** - Tamil STT
- **Edge-TTS** - Tamil TTS
- **BeautifulSoup** - Web scraping
- **DuckDuckGo Search** - Privacy-focused search

## Current Status

✅ Basic voice interface working  
✅ Speech-to-text in Tamil  
✅ Text-to-speech in Tamil  
✅ Local database search  
✅ Web crawler fallback  
✅ Conversational memory  

🚧 Working on:
- Adding more schemes to database
- Improving accuracy
- Better error handling
- Testing with real users

## Known Issues

- Sometimes STT struggles with heavy Tamil accents (working on it)
- Web crawler can be slow for complex govt sites
- Need to expand scheme database

## Why I Built This

During my final year, I noticed that many government schemes never reach the people who actually need them. The biggest barrier isn't eligibility - it's the complexity of accessing information. Most portals assume digital literacy that many Indians don't have.

Thozhan is my attempt to solve this by meeting people where they are - through voice, in their language.

## Notes

- Groq API is FREE to use (generous free tier)
- No data is stored - everything is in-memory
- STT/TTS processing happens locally
- **Never commit your `.env` file** - it has your API key!

## Contributing

This is still a work in progress! If you want to contribute:
- Fork it
- Create a branch
- Make your changes
- Submit a PR

Or just open an issue if you find bugs or have suggestions.

## License

MIT License - feel free to use this for your own projects!

---

Built as a demo project. Feedback welcome!
