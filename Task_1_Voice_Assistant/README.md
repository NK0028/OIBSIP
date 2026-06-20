#  ARIA - Adaptive Response Intelligence Assistant
### Oasis Infobyte Python Programming Internship | Task 1

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Speech](https://img.shields.io/badge/Speech-Recognition-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-success?style=for-the-badge)

---

##  Overview
ARIA (Adaptive Response Intelligence Assistant) is an advanced
Python-based voice assistant that listens to voice commands and
responds intelligently. Built as Task 1 of the Oasis Infobyte
Python Programming Internship, ARIA demonstrates real-world
application of speech recognition, NLP, API integration,
and object-oriented programming.

---

##  Features
| Feature | Description |
|--------|-------------|
| 🎙️ Voice Recognition | Captures and transcribes speech via Google Speech API |
| 🔊 Text-to-Speech | Responds verbally using pyttsx3 |
| 🌤️ Live Weather | Fetches real-time weather via OpenWeatherMap API |
| 📖 Wikipedia Search | Summarizes any topic from Wikipedia |
| 🌐 Browser Control | Opens websites and performs Google searches by voice |
| 📧 Email Sender | Composes and sends emails entirely by voice |
| 🕐 Time & Date | Reports current time, date, and day of week |
| 😄 Jokes | Tells programming jokes on demand |
| 🔒 Secure Config | Credentials stored in .env, never hardcoded |

---

##  Tech Stack
- **Language:** Python 3.x
- **Speech Input:** SpeechRecognition + PyAudio
- **Speech Output:** pyttsx3
- **Weather API:** OpenWeatherMap
- **Knowledge Base:** Wikipedia API
- **Email:** smtplib + Gmail SMTP
- **Security:** python-dotenv

---

##  Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/NK0028/OIBSIP.git
cd OIBSIP/Task_1_Voice_Assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    # Mac/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
WEATHER_API_KEY=your_openweathermap_api_key

EMAIL_ADDRESS=your_email@gmail.com

EMAIL_PASSWORD=your_gmail_app_password

### 5. Run ARIA
```bash
python main.py
```

---

##  Voice Commands

| Say This | ARIA Does This |
|----------|----------------|
| "Hello" / "Hi" | Greets you based on time of day |
| "What's the time?" | Tells current time |
| "What's today's date?" | Tells today's date |
| "Search Wikipedia for Python" | Summarizes Python on Wikipedia |
| "What's the weather?" | Fetches live Peshawar weather |
| "Open YouTube" | Opens YouTube in browser |
| "Send email" | Guides you through email by voice |
| "Tell me a joke" | Tells a programming joke |
| "Who are you?" | ARIA introduces herself |
| "Exit" / "Goodbye" | Shuts down ARIA |

---

##  Project Structure
Task_1_Voice_Assistant/

├── main.py              # Core assistant logic

├── requirements.txt     # Python dependencies

├── .env                 # Secret keys (not pushed to GitHub)

├── .gitignore           # Ignores .env and venv

└── README.md            # Project documentation

---

##  Security
- All API keys and credentials are stored in a `.env` file
- `.env` is listed in `.gitignore` and never pushed to GitHub
- Gmail uses App Password instead of real account password

---

##  Requirements
SpeechRecognition

pyttsx3

requests

wikipedia

pyaudio

python-dotenv

---

##  Internship Details
- **Organization:** Oasis Infobyte
- **Domain:** Python Programming
- **Task:** 1 — Voice Assistant
- **Intern:** Naeem Khan
- **Duration of the task:** 15 June – 25 June 2026