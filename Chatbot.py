from groq import Groq                                # chatbot for answering 'general' query
from json import load, dump
import datetime
from dotenv import dotenv_values

import os
env_path = os.path.join(os.path.dirname(__file__), '.env')
env_vars = dotenv_values(env_path)

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key= GroqAPIKey)

base_dir = os.path.dirname(__file__)  # this gives path to RealtimeSearchEngine.py
chatlog_path = os.path.join(base_dir, "Data", "ChatLog.json")


messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

try:
    with open(chatlog_path, "r") as F:
        messages = load(F)
except FileNotFoundError:
    with open(chatlog_path, "w") as F:
        dump([], F)

def RealtimeInformation():
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

def answerModifier(answer):
    lines = answer.split('\n')          # split the response into lines
    non_empty_lines = [line for line in lines if line.strip()]      # removes empty lines
    modified_answer = '\n'.join(non_empty_lines)            # joins cleaned lines back together
    return modified_answer

def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response"""
    try:
        with open(chatlog_path, "r") as F:
            messages = load(F)
        messages.append({"role": "user", "content": f"{Query}"})
        completion = client.chat.completions.create(
            model = "llama3-70b-8192",
            messages = SystemChatBot + [{"role": "system", "content": RealtimeInformation()}]+ messages,
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

        return answerModifier(answer= answer)
    
    except Exception as e:
        print(f"Error: {e}")
        with open(chatlog_path, "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

if __name__ == "__main__":
    while True:
        user_input = input("Enter your Question:  ")
        print(ChatBot(user_input))
    