from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

import os
env_path = os.path.join(os.path.dirname(__file__), '.env')
env_vars = dotenv_values(env_path) # to make elements of .env to key value pairs

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key= GroqAPIKey)

base_dir = os.path.dirname(__file__)  # this gives path to RealtimeSearchEngine.py
chatlog_path = os.path.join(base_dir, "Data", "ChatLog.json")

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

try:
    with open(chatlog_path, "r") as f:
        messages = load(f)
except:
    with open(chatlog_path, "r") as f:
        dump([], f)

def GoogleSearch(query):
    results = list(search(query, advanced= True, num_results=5))
    answer = f"Search results for '{query}' are:\n[start]\n"

    for i in results:
        answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    
    answer += "[end]"
    return answer

def answerModifier(answer):
    lines = answer.split('\n')          # split the response into lines
    non_empty_lines = [line for line in lines if line.strip()]      # removes empty lines
    modified_answer = '\n'.join(non_empty_lines)            # joins cleaned lines back together
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    data= ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed, \n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} Hours:{minute} Minutes :{second} Seconds\n"

    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    with open(chatlog_path, "r") as f:
        messages = load(f)
    
    messages.append({"role": "user", "content": f"{prompt}"})

    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model = "llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        max_tokens=1024,
            temperature=0.7,
            top_p=  1,
            stream= True,
            stop = None
    
    )

    answer = ""

    for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
    answer = answer.replace("</s>", "")

    messages.append({"role": "assistant", "content": answer})

    with open(chatlog_path, "w") as f:
            dump(messages, f, indent=4)

    SystemChatBot.pop()
    return answerModifier(answer= answer)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your Query:  ")
        print(RealtimeSearchEngine(prompt))