import time, os, json, threading, requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
TARGET = '_anu_.xree'
DATA_FILE = f"{TARGET}_data.json"
LOG_FILE = "log.txt"
WEEKLY_FILE = f"{TARGET}_weekly.txt"

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
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                old_data = json.load(f)
        else:
            old_data = {"followers": [], "following": []}

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # Login
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)
        driver.find_element(By.NAME, 'username').send_keys(IG_USERNAME)
        driver.find_element(By.NAME, 'password').send_keys(IG_PASSWORD + Keys.RETURN)
        time.sleep(7)

        # Navigate to target profile
        driver.get(f"https://www.instagram.com/{TARGET}/")
        time.sleep(5)

        # Get followers/following counts
        followers_button = driver.find_element(By.XPATH, "//a[contains(@href,'/followers')]")
        following_button = driver.find_element(By.XPATH, "//a[contains(@href,'/following')]")

        followers_count = followers_button.text.split("\n")[0]
        following_count = following_button.text.split("\n")[0]

        new_followers = [f"Follower count: {followers_count}"]
        new_following = [f"Following count: {following_count}"]

        added_followers = list(set(new_followers) - set(old_data['followers']))
        removed_followers = list(set(old_data['followers']) - set(new_followers))
        added_following = list(set(new_following) - set(old_data['following']))
        removed_following = list(set(old_data['following']) - set(new_following))

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

        send(msg)
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n" + "-"*50 + "\n")

        with open(DATA_FILE, "w") as f:
            json.dump({"followers": new_followers, "following": new_following}, f)

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
    except Exception as e:
        send(f"❌ IG Tracker Error: {e}")

# === Run the tracker in background ===
threading.Thread(target=run_tracker).start()

# === Dummy Flask server to keep Render awake ===
app = Flask(__name__)
@app.route('/')
def home():
    return "✅ IG Selenium Tracker Running"

app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
