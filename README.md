# Thozhan – Voice-First Tamil Government Assistant

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
