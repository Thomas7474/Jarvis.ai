from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep


import os

# Add at the top of SpeechToText.py
def start_voice_server():
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    import threading

    def run_server():
        os.chdir(os.path.join(os.path.dirname(__file__), "Data"))
        server = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
        print("Serving at http://localhost:8000")
        server.serve_forever()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()







env_path = os.path.join(os.path.dirname(__file__), '.env')
env_vars = dotenv_values(env_path)
InputLanguage = env_vars.get("InputLanguage")

HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

base_dir = os.path.dirname(__file__)  # this gives path to RealtimeSearchEngine.py
voice_path = os.path.join(base_dir, "Data", "Voice.html")


HtmlCode = str(HtmlCode).replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

with open(voice_path, "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()




chrome_options = Options()

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/89.0.4389.90 Safari/537.36"
)
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
#chrome_options.add_argument("--headless=new")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

TempDirPath = rf"{current_dir}/Frontend/Files"

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w",   encoding='utf-8') as file:
        file.write(Status)

import string

def QueryModifier(Query):
    new_query = Query.strip().lower()

    # Remove trailing punctuation for clean check
    if new_query and new_query[-1] in ".!?":
        new_query = new_query[:-1]

    # Check if it starts with a known question phrase
    question_words = [
        "how", "what", "when", "who", "where", "can you", "could you", "will you",
        "would you", "why", "is you", "are you", "whom", "whose", "was it", "was you"
    ]

    is_question = any(new_query.startswith(q) for q in question_words)

    # Add proper punctuation
    if is_question:
        new_query += "?"
    else:
        new_query += "."

    return new_query.capitalize()


def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

import time
import requests

def wait_until_server_is_ready(url, timeout=5):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.5)
    raise Exception("Server not ready.")

import time

def SpeechRecognition():
    wait_until_server_is_ready("http://localhost:8000/Voice.html")
    driver.get("http://localhost:8000/Voice.html")

    wait = WebDriverWait(driver, 10)
    start_button = wait.until(EC.element_to_be_clickable((By.ID, "start")))
    start_button.click()

    timeout = 15  # max 15 seconds to listen
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            text = driver.find_element(By.ID, "output").text.strip()
            if text:
                driver.find_element(By.ID, "end").click()
                if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                    return QueryModifier(text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(text))
        except Exception as e:
            pass
        time.sleep(0.5)  # allow time for JS to update DOM

    SetAssistantStatus("No speech detected.")
    return ""



if __name__=="__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)   