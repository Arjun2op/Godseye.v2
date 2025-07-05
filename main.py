import time
import os
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

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
TARGET = '_anu_.xree'  # Change this to your target username
DATA_FILE = f"{TARGET}_data.json"
LOG_FILE = "log.txt"
WEEKLY_FILE = f"{TARGET}_weekly.txt"

# === CHROME SETUP ===
CHROME_BINARY = "/opt/render/project/.render/chrome/chrome"
CHROMEDRIVER_PATH = "/opt/render/project/.render/chromedriver/chromedriver"

# === Send Telegram Message ===
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

# === IG Tracker ===
def run_tracker():
    while True:
        try:
            # Load previous data
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as f:
                    old_data = json.load(f)
            else:
                old_data = {"followers": [], "following": []}

            # Configure Chrome options
            options = Options()
            options.binary_location = CHROME_BINARY
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--remote-debugging-port=9222')
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Initialize WebDriver
            service = Service(executable_path=CHROMEDRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Login to Instagram
            driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(5)
            
            # Accept cookies if popup appears
            try:
                cookie_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow essential and optional cookies')]"))
                )
                cookie_button.click()
                time.sleep(2)
            except:
                pass

            # Fill login form
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, 'username'))
            )
            password_field = driver.find_element(By.NAME, 'password')
            
            username_field.send_keys(IG_USERNAME)
            password_field.send_keys(IG_PASSWORD + Keys.RETURN)
            time.sleep(7)

            # Handle "Save Login Info" popup if appears
            try:
                not_now_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Not now')]"))
                )
                not_now_button.click()
                time.sleep(2)
            except:
                pass

            # Navigate to target profile
            driver.get(f"https://www.instagram.com/{TARGET}/")
            time.sleep(5)

            # Get followers/following counts
            followers_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/followers')]"))
            )
            following_button = driver.find_element(By.XPATH, "//a[contains(@href,'/following')]")

            followers_count = followers_button.text.split()[0]
            following_count = following_button.text.split()[0]

            new_followers = [f"Follower count: {followers_count}"]
            new_following = [f"Following count: {following_count}"]

            # Compare with old data
            added_followers = list(set(new_followers) - set(old_data['followers']))
            removed_followers = list(set(old_data['followers']) - set(new_followers))
            added_following = list(set(new_following) - set(old_data['following']))
            removed_following = list(set(old_data['following']) - set(new_following))

            # Prepare message
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            msg = f"📊 IG Tracker Update for @{TARGET}\n🕒 {now}\n"
            if added_followers:
                msg += f"\n🟢 New Followers:\n" + "\n".join(added_followers[:10])
            if removed_followers:
                msg += f"\n🔴 Unfollowed You:\n" + "\n".join(removed_followers[:10])
            if added_following:
                msg += f"\n👣 You Followed:\n" + "\n".join(added_following[:10])
            if removed_following:
                msg += f"\n❌ You Unfollowed:\n" + "\n".join(removed_following[:10])
            if msg.strip() == f"📊 IG Tracker Update for @{TARGET}\n🕒 {now}":
                msg += "\n✅ No changes detected."

            # Send message and save data
            send(msg)
            with open(LOG_FILE, "a") as f:
                f.write(msg + "\n" + "-"*50 + "\n")

            with open(DATA_FILE, "w") as f:
                json.dump({"followers": new_followers, "following": new_following}, f)

            # Weekly Report (Sunday only)
            if datetime.now().weekday() == 6:
                weekly_msg = f"📅 Weekly Report for @{TARGET} - {datetime.now().strftime('%Y-%m-%d')}\n\n"
                weekly_msg += f"👥 Followers:\n" + "\n".join(new_followers)
                weekly_msg += f"\n\n👣 Following:\n" + "\n".join(new_following)
                with open(WEEKLY_FILE, "w") as f:
                    f.write(weekly_msg)
                if len(weekly_msg) < 4000:
                    send(weekly_msg)
                else:
                    send("📎 Weekly report too long, saved in file.")

            driver.quit()

            # Wait for 1 hour before next check
            time.sleep(3600)

        except Exception as e:
            error_msg = f"❌ IG Tracker Error: {str(e)}"
            print(error_msg)
            send(error_msg)
            time.sleep(600)  # Wait 10 minutes before retrying after error

# === Start Tracker in Background ===
threading.Thread(target=run_tracker, daemon=True).start()

# === Dummy Web Server (keeps Render running) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "IG Selenium Tracker Running"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
