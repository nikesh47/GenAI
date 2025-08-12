# Python Package to handle voice functionalities
import speech_recognition as sr
from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv
from openai.helpers import LocalAudioPlayer
import asyncio

load_dotenv()  # Load environment variables from .env file

from graph import graph
import os


openai = AsyncOpenAI()

async def tts(text: str):
    async with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="coral",
        input=text,
        instructions="Speak in a normal and professional tone",
        response_format="pcm"
    ) as response:
        await LocalAudioPlayer().play(response)



def main():
    r = sr.Recognizer() # Speech Recognizer Instance to handle audio input to text

    with sr.Microphone() as source:   # Mic Access
        r.adjust_for_ambient_noise(source)
        r.pause_threshold = 2  # Wait for 2 seconds of silence
        
        while True:
            print("Listening........ Please speak something.")
            audio = r.listen(source)

            try:
                stt = r.recognize_google(audio)
                print("You said: ", stt)
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio. Please try again.")
                continue



            for event in graph.stream({ "role": "assistant", "content": stt }, stream_mode="values"):
                    if "messages" in event:
                        # messages.append({ "role": "assistant", "content": event["messages"][-1].content })
                        event["messages"][-1].pretty_print()

main()

# asyncio.run(tts(text="Hey! (laugh) Nice to meet you. How can I help you with coding"))