# ════════════════════════════════════════════════════════════════
#   ARIA - Adaptive Response Intelligence Assistant
#   Author  : Naeem (Oasis Infobyte Internship — Task 1)
#   Version : 2.0
#   Stack   : Python | SpeechRecognition | pyttsx3 | OpenWeather
# ════════════════════════════════════════════════════════════════

import speech_recognition as sr
from dotenv import load_dotenv
import pyttsx3
import datetime
import wikipedia
import webbrowser
import requests
import smtplib
import random
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── ARIA Configuration ────────────────────────────────────────────
load_dotenv()  

ASSISTANT_NAME  = "Aria"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DEFAULT_CITY    = "Peshawar"
EMAIL_ADDRESS   = os.getenv("EMAIL_ADDRESS")    # this method is used to keep personal information confidential
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD") 

# ── Boot-up Greetings (randomized — unique touch) ─────────────────
BOOT_MESSAGES = [
    f"Hello! {ASSISTANT_NAME} is online and ready to assist you.",
    f"Good to see you! {ASSISTANT_NAME} at your service.",
    f"Systems ready. I'm {ASSISTANT_NAME}. What do you need?",
    f"{ASSISTANT_NAME} activated. Let's get things done.",
]

# ── Time-based greeting helper ────────────────────────────────────
def get_time_greeting() -> str:
    hour = datetime.datetime.now().hour
    if   hour < 12: return "Good morning"
    elif hour < 17: return "Good afternoon"
    else:           return "Good evening"

# ════════════════════════════════════════════════════════════════
#  CORE ENGINE  —  Speech I/O
# ════════════════════════════════════════════════════════════════

class VoiceEngine:
    """Handles all text-to-speech and speech-to-text operations."""

    def __init__(self):
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 165)
        self.tts.setProperty('volume', 0.95)
        voices = self.tts.getProperty('voices')
        # Pick a clear voice if available
        if voices:
            self.tts.setProperty('voice', voices[0].id)

    def respond(self, message: str):
        """Speak and print a response."""
        print(f"\n  [{ASSISTANT_NAME}] → {message}\n")
        self.tts.say(message)
        self.tts.runAndWait()

    def capture_voice(self, prompt: str = "") -> str | None:
        """Listen to microphone and return transcribed text."""
        mic = sr.Recognizer()
        mic.pause_threshold    = 0.8
        mic.dynamic_energy_threshold = True

        if prompt:
            self.respond(prompt)

        with sr.Microphone() as source:
            print("  🎙  Listening...", end=" ", flush=True)
            mic.adjust_for_ambient_noise(source, duration=0.4)
            try:
                raw_audio = mic.listen(source, timeout=6, phrase_time_limit=10)
                transcript = mic.recognize_google(raw_audio, language="en-US")
                print(f"Heard: '{transcript}'")
                return transcript.lower().strip()

            except sr.WaitTimeoutError:
                self.respond("I didn't catch anything. Please speak again.")
            except sr.UnknownValueError:
                self.respond("Couldn't make that out. Mind repeating?")
            except sr.RequestError:
                self.respond("Speech service is unreachable right now.")
            return None


# ════════════════════════════════════════════════════════════════
#  SKILL MODULES  —  Individual Features
# ════════════════════════════════════════════════════════════════

class SkillSet:
    """
    Contains all assistant capabilities as isolated methods.
    Each skill is self-contained and independently testable.
    """

    def __init__(self, engine: VoiceEngine):
        self.engine = engine

    # ── Date & Time ──────────────────────────────────────────────
    def current_time(self):
        stamp = datetime.datetime.now().strftime("%I:%M %p")
        self.engine.respond(f"It is currently {stamp}.")

    def current_date(self):
        stamp = datetime.datetime.now().strftime("%A, %d %B %Y")
        self.engine.respond(f"Today is {stamp}.")

    def day_of_week(self):
        day = datetime.datetime.now().strftime("%A")
        self.engine.respond(f"Today is {day}.")

    # ── Wikipedia Knowledge ───────────────────────────────────────
    def wiki_lookup(self, raw_query: str):
        topic = raw_query.replace("wikipedia", "").replace("search", "").strip()
        if not topic:
            self.engine.respond("What topic should I search on Wikipedia?")
            return
        self.engine.respond(f"Looking up {topic} on Wikipedia...")
        try:
            summary = wikipedia.summary(topic, sentences=3, auto_suggest=True)
            self.engine.respond(summary)
        except wikipedia.exceptions.DisambiguationError as e:
            self.engine.respond(
                f"Multiple results found for {topic}. "
                f"Try being more specific. For example: {e.options[0]}."
            )
        except wikipedia.exceptions.PageError:
            self.engine.respond(f"No Wikipedia page found for {topic}.")
        except Exception:
            self.engine.respond("Something went wrong with the Wikipedia search.")

    # ── Weather ──────────────────────────────────────────────────
    def fetch_weather(self, city: str = DEFAULT_CITY):
        endpoint = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )
        try:
            data     = requests.get(endpoint, timeout=5).json()
            if data.get("cod") != 200:
                self.engine.respond(f"I couldn't find weather data for {city}.")
                return
            temp     = data["main"]["temp"]
            feels    = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            condition= data["weather"][0]["description"]
            self.engine.respond(
                f"In {city}, it's {condition} with {temp}°C. "
                f"Feels like {feels}°C and humidity is {humidity} percent."
            )
        except requests.exceptions.Timeout:
            self.engine.respond("Weather request timed out. Check your connection.")
        except Exception:
            self.engine.respond("Unable to retrieve weather information right now.")

    # ── Browser Control ──────────────────────────────────────────
    def launch_site(self, query: str):
        site_map = {
            "youtube"   : "https://www.youtube.com",
            "google"    : "https://www.google.com",
            "github"    : "https://www.github.com",
            "gmail"     : "https://mail.google.com",
            "linkedin"  : "https://www.linkedin.com",
            "stackoverflow": "https://stackoverflow.com",
            "chatgpt"   : "https://chat.openai.com",
        }
        for name, link in site_map.items():
            if name in query:
                self.engine.respond(f"Opening {name} in your browser.")
                webbrowser.open(link)
                return
        # Fallback: Google search
        search_query = query.replace("open", "").replace("search for", "").strip()
        if search_query:
            self.engine.respond(f"Searching Google for {search_query}.")
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        else:
            self.engine.respond("Which website should I open?")

    # ── Email Composer ───────────────────────────────────────────
    def compose_and_send_email(self, to: str, subject: str, body: str):
        try:
            msg                    = MIMEMultipart()
            msg["From"]            = EMAIL_ADDRESS
            msg["To"]              = to
            msg["Subject"]         = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as session:
                session.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                session.sendmail(EMAIL_ADDRESS, to, msg.as_string())

            self.engine.respond(f"Email successfully sent to {to}.")
        except smtplib.SMTPAuthenticationError:
            self.engine.respond("Email authentication failed. Check your credentials.")
        except Exception as e:
            self.engine.respond(f"Could not send email. Error: {str(e)}")

    # ── System Controls ──────────────────────────────────────────
    def tell_joke(self):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
            "Why did the developer go broke? Because he used up all his cache.",
            "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
        ]
        self.engine.respond(random.choice(jokes))

    def self_intro(self):
        self.engine.respond(
            f"I'm {ASSISTANT_NAME}, an AI voice assistant built with Python "
            f"by Naeem as part of the Oasis Infobyte internship. "
            f"I can tell you the time, search Wikipedia, check weather, "
            f"open websites, send emails, and more."
        )


# ════════════════════════════════════════════════════════════════
#  COMMAND ROUTER  —  Intent Matching
# ════════════════════════════════════════════════════════════════

class CommandRouter:
    """
    Routes voice input to the correct skill.
    Uses keyword-based intent detection with priority ordering.
    """

    def __init__(self, engine: VoiceEngine, skills: SkillSet):
        self.engine = engine
        self.skills = skills

    def route(self, query: str):
        if not query:
            return

        # ── Greetings ────────────────────────────────────────────
        if any(w in query for w in ["hello", "hi", "hey", "good morning",
                                     "good afternoon", "good evening"]):
            greeting = get_time_greeting()
            self.engine.respond(f"{greeting}! How can I assist you today?")

        # ── Identity ─────────────────────────────────────────────
        elif any(w in query for w in ["who are you", "your name",
                                       "what are you", "introduce yourself"]):
            self.skills.self_intro()

        # ── Time & Date ──────────────────────────────────────────
        elif "time" in query:
            self.skills.current_time()

        elif "date" in query or "today" in query:
            self.skills.current_date()

        elif "day" in query:
            self.skills.day_of_week()

        # ── Wikipedia ────────────────────────────────────────────
        elif any(w in query for w in ["wikipedia", "who is", "what is",
                                       "tell me about", "search"]):
            self.skills.wiki_lookup(query)

        # ── Weather ──────────────────────────────────────────────
        elif "weather" in query or "temperature" in query or "forecast" in query:
            self.skills.fetch_weather(DEFAULT_CITY)

        # ── Email ────────────────────────────────────────────────
        elif "email" in query or "send mail" in query:
            recipient = self.engine.capture_voice("Who is the recipient's email address?")
            subject   = self.engine.capture_voice("What is the subject of the email?")
            body      = self.engine.capture_voice("What message should I include?")
            if all([recipient, subject, body]):
                self.skills.compose_and_send_email(recipient, subject, body)
            else:
                self.engine.respond("Email cancelled due to missing information.")

        # ── Browser ──────────────────────────────────────────────
        elif "open" in query or "launch" in query or "go to" in query:
            self.skills.launch_site(query)

        # ── Joke ─────────────────────────────────────────────────
        elif "joke" in query or "funny" in query or "make me laugh" in query:
            self.skills.tell_joke()

        # ── Exit ─────────────────────────────────────────────────
        elif any(w in query for w in ["exit", "quit", "bye",
                                       "goodbye", "shut down", "stop"]):
            self.engine.respond(f"Goodbye! {ASSISTANT_NAME} signing off. Have a great day!")
            sys.exit(0)

        # ── Fallback ─────────────────────────────────────────────
        else:
            self.engine.respond(
                "I'm not sure how to help with that yet. "
                "Try asking about the weather, time, or Wikipedia."
            )


# ════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ════════════════════════════════════════════════════════════════

def launch_aria():
    engine = VoiceEngine()
    skills = SkillSet(engine)
    router = CommandRouter(engine, skills)

    # Boot greeting
    engine.respond(random.choice(BOOT_MESSAGES))

    # Main loop
    while True:
        user_input = engine.capture_voice()
        if user_input:
            router.route(user_input)

if __name__ == "__main__":
    launch_aria()