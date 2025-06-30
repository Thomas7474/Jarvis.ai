import pygame      # for audio playback
import random
import asyncio
import edge_tts    # for text to speech functionality
import os
from dotenv import dotenv_values


env_path = os.path.join(os.path.dirname(__file__), '.env')
env_vars = dotenv_values(env_path)
AssistantVoice = env_vars.get("AssistantVoice")

base_dir = os.path.dirname(__file__)  # this gives path to RealtimeSearchEngine.py
speech_path = os.path.join(base_dir, "Data", "speech.mp3")


async def TextToAudioFile(text)->None:
    file_path= speech_path

    if os.path.exists(file_path):
        os.remove(file_path)
    
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch= '+5Hz', rate= '+13%')
    await communicate.save(speech_path)               # convert text to audio file
  
def TTS(Text, func=lambda r=None: True ):
    while True:
        try:
            asyncio.run(TextToAudioFile(Text))
            pygame.mixer.init()                 # Initializes the audio system for playback.
            pygame.mixer.music.load(speech_path)     # Loads the MP3 file.
            pygame.mixer.music.play()                   	# Starts playing the audio

            while pygame.mixer.music.get_busy():        
                if func() == False:                  # loops (starts after the playback starts) wait till the playback stops (false means stop unnaturally)
                    break
                
                pygame.time.Clock().tick(10)            # slows down the loop to 10 iterations per second

            return True
        except Exception as e:
            print("Error in TTS: {e}")
        
        finally:
            try:
                func(False)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            
            except Exception as e:
                print("Error in finally block: {e}")

def TextToSpeech(Text, func= lambda r=None: True):
    Data = str(Text).split(".")

    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

    if len(Data)>4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".")[0:2])+ ". " + random.choices(responses), func )

    else:
        TTS(Text, func)


if __name__== "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))