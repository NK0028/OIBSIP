# ════════════════════════════════════════════════════════════════
#   ARIA - Adaptive Response Intelligence Assistant
#   Author  : Naeem (Oasis Infobyte Internship — Task 1)
#   Version : 3.0
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
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── ARIA Configuration ────────────────────────────────────────────
load_dotenv()

ASSISTANT_NAME  = "Aria"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DEFAULT_CITY    = "Peshawar"
EMAIL_ADDRESS   = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD")

# ── Boot-up Greetings (randomized) ───────────────────────────────
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

        # Print all voices so you can pick your preferred one
        for i, voice in enumerate(voices):
            print(f"Voice {i}: {voice.name} | ID: {voice.id}")

        # Change index to switch voice (0, 1, 2 etc.)
        if voices:
            self.tts.setProperty('voice', voices[4].id)

    def respond(self, message: str):
        """Speak and print a response."""
        print(f"\n  [{ASSISTANT_NAME}] → {message}\n")
        self.tts.say(message)
        self.tts.runAndWait()

    def capture_voice(self, prompt: str = "") -> str | None:
        """Listen to microphone and return transcribed text."""
        mic = sr.Recognizer()
        mic.energy_threshold         = 300
        mic.dynamic_energy_threshold = True
        mic.pause_threshold          = 0.8

        if prompt:
            self.respond(prompt)

        with sr.Microphone() as source:
            print("  🎙  Listening...", end=" ", flush=True)
            mic.adjust_for_ambient_noise(source, duration=0.5)
            try:
                raw_audio  = mic.listen(source, timeout=8, phrase_time_limit=8)
                transcript = mic.recognize_google(raw_audio, language="en-US")
                print(f"Heard: '{transcript}'")
                return transcript.lower().strip()

            except sr.WaitTimeoutError:
                print("Timeout — no speech detected.")
                return None                          # silent, no speaking
            except sr.UnknownValueError:
                print("Could not understand audio.")
                return None                          # silent, no speaking
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
        # Clean all trigger words from query
        remove_words = ["wikipedia", "search", "tell me about",
                        "who is", "what is", "look up", "find"]
        topic = raw_query
        for word in remove_words:
            topic = topic.replace(word, "").strip()

        if not topic:
            self.engine.respond("What topic should I search on Wikipedia?")
            return

        self.engine.respond(f"Looking up {topic}.")

        try:
            wikipedia.set_lang("en")
            results = wikipedia.search(topic, results=3)

            if not results:
                self.engine.respond(f"No results found for {topic}.")
                return

            # Try top results with fallback
            for result in results[:2]:
                try:
                    summary = wikipedia.summary(
                        result,
                        sentences=2,
                        auto_suggest=False,
                        redirect=True
                    )
                    self.engine.respond(summary)
                    return
                except wikipedia.exceptions.DisambiguationError:
                    continue
                except wikipedia.exceptions.PageError:
                    continue

            self.engine.respond(
                f"Couldn't find a clear result for {topic}. Try being more specific.")

        except Exception:
            self.engine.respond(
                f"Wikipedia search failed for {topic}. Please try again.")

    # ── Weather ──────────────────────────────────────────────────
    def fetch_weather(self, city: str = DEFAULT_CITY):
        endpoint = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )
        try:
            data      = requests.get(endpoint, timeout=5).json()
            if data.get("cod") != 200:
                self.engine.respond(f"I couldn't find weather data for {city}.")
                return
            temp      = data["main"]["temp"]
            feels     = data["main"]["feels_like"]
            humidity  = data["main"]["humidity"]
            condition = data["weather"][0]["description"]
            self.engine.respond(
                f"In {city}, it's {condition} with {temp} degrees Celsius. "
                f"Feels like {feels} degrees and humidity is {humidity} percent."
            )
        except requests.exceptions.Timeout:
            self.engine.respond("Weather request timed out. Check your connection.")
        except Exception:
            self.engine.respond("Unable to retrieve weather information right now.")

    # ── Browser Control ──────────────────────────────────────────
    def launch_site(self, query: str):
        site_map = {
            "youtube"      : "https://www.youtube.com",
            "google"       : "https://www.google.com",
            "github"       : "https://www.github.com",
            "gmail"        : "https://mail.google.com",
            "linkedin"     : "https://www.linkedin.com",
            "stackoverflow": "https://stackoverflow.com",
            "chatgpt"      : "https://chat.openai.com",
        }
        for name, link in site_map.items():
            if name in query:
                self.engine.respond(f"Opening {name} in your browser.")
                webbrowser.open(link)
                return

        # Fallback: Google search
        search_query = (query.replace("open", "")
                            .replace("launch", "")
                            .replace("go to", "")
                            .replace("search for", "")
                            .strip())
        if search_query:
            self.engine.respond(f"Searching Google for {search_query}.")
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        else:
            self.engine.respond("Which website should I open?")

    # ── Email Composer ───────────────────────────────────────────
    def compose_and_send_email(self, to: str, subject: str, body: str):
        try:
            msg            = MIMEMultipart()
            msg["From"]    = EMAIL_ADDRESS
            msg["To"]      = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as session:
                session.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                session.sendmail(EMAIL_ADDRESS, to, msg.as_string())

            self.engine.respond(f"Email successfully sent to {to}.")
        except smtplib.SMTPAuthenticationError:
            self.engine.respond(
                "Email authentication failed. Check your credentials in the env file.")
        except Exception as e:
            self.engine.respond(f"Could not send email. Error: {str(e)}")

    # ── Jokes ────────────────────────────────────────────────────
    def tell_joke(self):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
            "Why did the developer go broke? Because he used up all his cache.",
            "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
            "Why do Java developers wear glasses? Because they don't C sharp!",
        ]
        self.engine.respond(random.choice(jokes))

    # ── Self Introduction ────────────────────────────────────────
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
    Uses keyword-based intent detection with strict priority ordering.
    """

    def __init__(self, engine: VoiceEngine, skills: SkillSet):
        self.engine = engine
        self.skills = skills

    def route(self, query: str):
        if not query or len(query.strip()) < 2:
            return

        print(f"\n  Routing: '{query}'")

        # ── Greetings ────────────────────────────────────────────
        if any(w in query for w in ["hello", "hi", "hey"]):
            greeting = get_time_greeting()
            self.engine.respond(f"{greeting}! How can I assist you?")

        # ── Identity ─────────────────────────────────────────────
        elif any(w in query for w in ["who are you", "your name",
                                       "what are you", "introduce"]):
            self.skills.self_intro()

        # ── Time (before date to avoid conflict) ─────────────────
        elif "time" in query and "date" not in query:
            self.skills.current_time()

        # ── Date ─────────────────────────────────────────────────
        elif any(w in query for w in ["date", "today", "month", "year"]):
            self.skills.current_date()

        # ── Day ──────────────────────────────────────────────────
        elif "day" in query:
            self.skills.day_of_week()

        # ── Weather (before wikipedia to avoid conflict) ──────────
        elif any(w in query for w in ["weather", "temperature",
                                       "forecast", "hot", "cold", "humid"]):
            self.skills.fetch_weather(DEFAULT_CITY)

        # ── Wikipedia ────────────────────────────────────────────
        elif any(w in query for w in ["wikipedia", "who is", "what is",
                                       "tell me about", "search", "look up"]):
            self.skills.wiki_lookup(query)

        # ── Email ────────────────────────────────────────────────
        elif any(w in query for w in ["email", "send mail", "send message"]):
            recipient = self.engine.capture_voice(
                "What is the recipient's email address?")
            subject   = self.engine.capture_voice(
                "What is the subject?")
            body      = self.engine.capture_voice(
                "What is the message?")
            if all([recipient, subject, body]):
                self.skills.compose_and_send_email(recipient, subject, body)
            else:
                self.engine.respond("Email cancelled due to missing information.")

        # ── Browser ──────────────────────────────────────────────
        elif any(w in query for w in ["open", "launch", "go to", "browse"]):
            self.skills.launch_site(query)

        # ── Joke ─────────────────────────────────────────────────
        elif any(w in query for w in ["joke", "funny", "laugh", "humor"]):
            self.skills.tell_joke()

        # ── Exit ─────────────────────────────────────────────────
        elif any(w in query for w in ["exit", "quit", "bye",
                                       "goodbye", "shut down", "stop"]):
            self.engine.respond(
                f"Goodbye! {ASSISTANT_NAME} signing off. Have a great day!")
            sys.exit(0)

        # ── Fallback ─────────────────────────────────────────────
        else:
            self.engine.respond(
                "I didn't catch that clearly. "
                "Try asking about weather, time, or Wikipedia."
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

    # Main loop — never crashes, always keeps listening
    while True:
        try:
            user_input = engine.capture_voice()
            if user_input:
                router.route(user_input)
            time.sleep(0.3)       # small pause prevents overlapping audio

        except KeyboardInterrupt:
            engine.respond("Shutting down. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"  Loop error: {e}")
            continue              # recover from any unexpected error

if __name__ == "__main__":
    launch_aria()