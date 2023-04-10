import os
from playsound import playsound
import requests
from config import Config
cfg = Config()
import gtts


# TODO: Nicer names for these ids
voices = ["ErXwobaYiN019PkySvjV", "EXAVITQu4vr4xnSDxMaL"]

tts_headers = {
    "Content-Type": "application/json",
    "xi-api-key": cfg.elevenlabs_api_key
}

def eleven_labs_speech(text, voice_index=0):
    """Speak text using elevenlabs.io's API"""
    tts_url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}".format(
        voice_id=voices[voice_index])
    formatted_message = {"text": text}
    proxies = {}
    if cfg.elevenlabs_api_proxy is None:
        pass
    elif isinstance(cfg.elevenlabs_api_proxy, str):
        proxies = {"http": cfg.elevenlabs_api_proxy, "https": cfg.elevenlabs_api_proxy}
    elif isinstance(cfg.elevenlabs_api_proxy, dict):
        proxies = cfg.elevenlabs_api_proxy
    else:
        pass
    response = requests.post(
        tts_url, headers=tts_headers, json=formatted_message, proxies=proxies)

    if response.status_code == 200:
        with open("speech.mpeg", "wb") as f:
            f.write(response.content)
        playsound("speech.mpeg")
        os.remove("speech.mpeg")
        return True
    else:
        print("Request failed with status code:", response.status_code)
        print("Response content:", response.content)
        return False

def gtts_speech(text):
    tts = gtts.gTTS(text)
    tts.save("speech.mp3")
    playsound("speech.mp3")
    os.remove("speech.mp3")

def say_text(text, voice_index=0):
    if not cfg.elevenlabs_api_key:
        gtts_speech(text)
    else:
        success = eleven_labs_speech(text, voice_index)
        if not success:
            gtts_speech(text)

