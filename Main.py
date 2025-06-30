from Frontend.GUI import(
    GraphicalUserInterface,
    setAssistantStatus,
    showTextToScreen,
    tempDirectoryPath,
    setMicrophoneStatus,
    answerModifier,
    QueryModifier,
    getMicrophoneStatus,
    getAssistantStatus
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech 

from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os
import sys

env_path = os.path.join(os.path.dirname(__file__), 'Backend', '.env') # important 

# Step 2: Load the environment variables
env_vars = dotenv_values(env_path)

base_dir = os.path.dirname(__file__)
chatlog_path = os.path.join(base_dir, "Backend", "Data", "ChatLog.json")

# Step 3: Get the value of Assistantname
Assistantname = env_vars.get("Assistantname")
Username = env_vars.get("Username")
DefaultMessage = f'''{Username}: Hello {Assistantname}, How are you?
                 {Assistantname}: Welcome {Username}. I am doing well. How may I help you? '''
subprocesses= []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfnoChats():
    with open(chatlog_path, "r", encoding= 'utf-8') as File:
     if len(File.read())<5:
        with open(tempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")

        with open(tempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(chatlog_path, "r", encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] =="user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog= formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog= formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(tempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
        file.write(answerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    with open(tempDirectoryPath('Database.data'), "r", encoding='utf-8') as File:
     Data = File.read()
     if len(str(Data))>0:
        lines= Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(tempDirectoryPath('Response.data'), "w", encoding= 'utf-8')
        File.write(result)
        File.close()


def InitialExecution():
    setMicrophoneStatus("False")
    showTextToScreen("")
    ShowDefaultChatIfnoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

from Backend.SpeechToText import start_voice_server
start_voice_server()

InitialExecution()

def MainExecution():

    TaskExecution= False
    
    setAssistantStatus("Listening...")

    from Backend.SpeechToText import start_voice_server
    start_voice_server()



    Query= SpeechRecognition()
    showTextToScreen(f"{Username}: {Query}")
    setAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision: {Decision}")
    print("")

    G= any([i for i in Decision if i.startswith("general ")])
    R= any([i for i in Decision if i.startswith("realtime")])

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general ") or i.startswith("realtime")]
    )

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(automation(list(Decision)))
                TaskExecution= True

    if G and R or R :
        setAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        showTextToScreen(f"Assistantname: {Answer}")
        setAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    
    else:
        for Queries in Decision:
            if "general" in Queries:
                setAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ", "")
                Answer= ChatBot(QueryModifier(QueryFinal))
                showTextToScreen(f"{Assistantname}: {Answer}")
                setAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            
            elif "realtime" in Queries:
                setAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                showTextToScreen(f"{Assistantname}: {Answer}")
                setAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                showTextToScreen(f"{Assistantname}: {Answer}")
                setAssistantStatus("Answering...")
                TextToSpeech(Answer)
                setAssistantStatus("Answering...")
                sys.exit(1)

def FirstThread():

    while True:
        CurrentStatus = getMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()

        else:
            AIStatus = getAssistantStatus()

            if "Availabe..." in AIStatus:
                sleep(0.1)

            else:
                setAssistantStatus("Available...")

def SecondThread():
        GraphicalUserInterface()


if __name__ == "__main__":
    thread2 = threading.Thread(target = FirstThread, daemon=True)
    thread2.start()
    SecondThread()






