import time, os, json, threading, requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from flask import Flask
from datetime import datetime

# === CONFIG ===
BOT_TOKEN      = os.getenv("BOT_TOKEN")
CHAT_ID        = os.getenv("CHAT_ID")
IG_USERNAME    = os.getenv("IG_USERNAME")
IG_PASSWORD    = os.getenv("IG_PASSWORD")
TARGET         = '_anu_.xree'
DATA_FILE      = f"{TARGET}_data.json"
LOG_FILE       = "log.txt"
WEEKLY_FILE    = f"{TARGET}_weekly.txt"

# === CHROME SETUP (for Selenium 4+) ===
CHROME_BINARY      = "/opt/render/project/.render/chrome/chrome"
CHROMEDRIVER_PATH  = "/opt/render/project/.render/chromedriver/chromedriver"

def create_driver():
    options = Options()
    options.binary_location = CHROME_BINARY
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # (add any other flags you prefer here)

    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# === Send Telegram Message ===
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg}
        )
    except Exception as e:
        print(f"Telegram Error: {e}")

# === IG Tracker ===
def run_tracker():
    try:
        # load previous data (or init)
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                old_data = json.load(f)
        else:
            old_data = {"followers": [], "following": []}

        driver = create_driver()

        # login
        driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)
        driver.find_element(By.NAME, 'username').send_keys(IG_USERNAME)
        driver.find_element(By.NAME, 'password').send_keys(IG_PASSWORD + Keys.RETURN)
        time.sleep(7)

        # profile
        driver.get(f"https://www.instagram.com/{TARGET}/")
        time.sleep(5)

        # counts
        followers_btn = driver.find_element(By.XPATH, "//a[contains(@href,'/followers')]")
        following_btn = driver.find_element(By.XPATH, "//a[contains(@href,'/following')]")
        new_followers = [f"Follower count: {followers_btn.text.split()[0]}"]
        new_following = [f"Following count: {following_btn.text.split()[0]}"]

        # diff
        added_f = list(set(new_followers) - set(old_data['followers']))
        rem_f   = list(set(old_data['followers']) - set(new_followers))
        added_fg= list(set(new_following)- set(old_data['following']))
        rem_fg  = list(set(old_data['following']) - set(new_following))

        # build message
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        msg = f"📊 IG Tracker @{TARGET} — {now}\n"
        if added_f:  msg += "\n🟢 New Followers:\n" + "\n".join(added_f)
        if rem_f:    msg += "\n🔴 Unfollowed You:\n" + "\n".join(rem_f)
        if added_fg: msg += "\n👣 You Followed:\n" + "\n".join(added_fg)
        if rem_fg:   msg += "\n❌ You Unfollowed:\n" + "\n".join(rem_fg)
        if not (added_f or rem_f or added_fg or rem_fg):
            msg += "\n✅ No changes detected."

        # send & log
        send(msg)
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n" + "-"*40 + "\n")
        with open(DATA_FILE, "w") as f:
            json.dump({"followers": new_followers, "following": new_following}, f)

        # weekly (Sunday)
        if datetime.now().weekday() == 6:
            weekly_msg = (
                f"📅 Weekly Report @{TARGET} — {datetime.now():%Y-%m-%d}\n\n"
                f"👥 Followers:\n" + "\n".join(new_followers) +
                f"\n\n👣 Following:\n" + "\n".join(new_following)
            )
            with open(WEEKLY_FILE, "w") as f:
                f.write(weekly_msg)
            send(weekly_msg if len(weekly_msg) < 4000 else "📎 Weekly report saved to file.")

        driver.quit()

    except Exception as e:
        send(f"❌ IG Tracker Error: {e}")

# start background thread
threading.Thread(target=run_tracker, daemon=True).start()

# dummy Flask to keep Render alive
app = Flask(__name__)
@app.route('/')
def home():
    return "IG Selenium Tracker Running"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000"))
