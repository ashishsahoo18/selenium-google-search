"""Voice input/output wrappers with useful errors."""

def listen() -> str:
    """Record one short query from the default microphone."""
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.4)
        audio = recognizer.listen(source, timeout=6, phrase_time_limit=12)
    return recognizer.recognize_google(audio)


def speak(text: str) -> None:
    """Speak a short status message without blocking the UI caller."""
    import pyttsx3
    engine = pyttsx3.init(); engine.say(text); engine.runAndWait()
