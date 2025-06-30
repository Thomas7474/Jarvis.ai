from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import asyncio
import os

import os
env_path = os.path.join(os.path.dirname(__file__), '.env')
env_vars = dotenv_values(env_path)
GroqAPIKey = env_vars.get("GroqAPIKey")

classes = ["zCubwf", "hgKE1c", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", 
           "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vlzY6d", 
           "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt", 
           "sXLaOe", "LWfFKe", "VQF4g", "qv3Wpe", "Kno-rdesc", "SPZz6b"]

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/89.0.4389.90 Safari/537.36"
)

client = Groq(api_key= GroqAPIKey)

professional_responses = [
    "Your satisfaction  is my top priority: feel free to reach out if there's anything else I can help you with."
    "I'm at your service for any additional questions or support you may need- don't hesitate to ask."
]

messages= []

SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You 're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

def GoogleSearch(Topic):
    search(Topic)
    return True

def Content(Topic):
  

    def OpenNotepad(file):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, file])

    def contentWriterAI(prompt):
        messages.append({"role":"user", "content":f"{prompt}"})

        completion = client.chat.completions.create(        # openAI 's api structure...also mimicked by other models too..
            model = "llama3-8b-8192",
            messages = SystemChatBot+ messages,
            max_tokens = 2048,
            temperature=0.7,
            top_p=1,
            stream= True,
            stop= None
        )

        Answer = ""

        for chunk in completion:
           if chunk.choices[0].delta.content:
                Answer = Answer + chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer
    
    Topic: str = Topic.replace("Content", "") # just removes the word "content" from prompt to male the prompt  natural
    contentByAI = contentWriterAI(Topic)

    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:  # creats a file in system with lowercase of contet
        file.write(contentByAI)
        file.close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")
    return True



def youtubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    return True

def playYoutube(query):
    playonyt(query)
    return True

def openApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest= True, output=True, throw_error= True)
        return True
    except:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [a['href'] for a in soup.select('div.yuRUbf > a') if a.get('href')]

        def search_google(query):
              url = f"https://www.google.com/search?q={query}"
              headers = {"User-Agent": user_agent }             # user agent helps to enter google webpage which even blocks bots
              response = sess.get(url, headers=headers)
                
              if response.status_code==200:
                  return response.text
              else:
                  print("Failed to retrieve search results.")
              return None
        
        html = search_google(app)

        links = extract_links(html)

        if links:
            print(f"🔗 Opening fallback link: {links[0]}")
            webbrowser.open(links[0])
        else:
            print("❌ No links found on fallback search.")

        return True
    


def closeApp(app):
    if "chrome" in app:
        pass                     # skip for chrome
    else:
        try:
            close(app, match_closest=True, throw_error=True, output=True)
            return True
        except:
            return False
        
async def TranslateAndExecute(commands: list[str]):

    funcs=[]

    for command in commands:
        if command.startswith("open "):
                if "open it " in command:
                    pass
                if "open file"== command:
                    pass
                else:
                    fun = asyncio.to_thread(openApp, command.removeprefix("open "))
                    funcs.append(fun)

        elif command.startswith("general "):
            pass

        elif command.startswith("realtime "):
            pass

        elif command.startswith("close "):
             fun = asyncio.to_thread(closeApp, command.removeprefix("close "))
             funcs.append(fun)

        elif  command.startswith("play "):
             fun = asyncio.to_thread(playYoutube, command.removeprefix("play "))
             funcs.append(fun)

        elif  command.startswith("content "):
             fun = asyncio.to_thread(Content, command.removeprefix("content "))
             funcs.append(fun)

        elif command.startswith("google search "):
             fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
             funcs.append(fun)

        elif command.startswith("youtube search "):
             fun = asyncio.to_thread(youtubeSearch, command.removeprefix("youtube search "))       # system functions not included
             funcs.append(fun)

        else:
            print(f"No Function Found for {command}")

    results = await asyncio.gather(*funcs)

    for result in results:
            yield result


async def automation(commands:list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True


        



