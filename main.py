import os
import time
import json
import threading
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

app = Flask(__name__)

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
TARGET = '_anu_.xree'

def get_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Use ChromeDriverManager with explicit ChromeType
    service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def run_tracker():
    while True:
        try:
            driver = get_driver()
            # Your Instagram tracking logic here
            driver.quit()
            time.sleep(3600)  # Check every hour
        except Exception as e:
            print(f"Error: {str(e)}")
            time.sleep(600)  # Wait 10 minutes on error

@app.route('/')
def home():
    return "IG Tracker Running"

if __name__ == '__main__':
    threading.Thread(target=run_tracker, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))
