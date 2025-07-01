#!/bin/bash

mkdir -p .render/chrome
mkdir -p .render/chromedriver

# Download Chrome
wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.60/linux64/chrome-linux64.zip -O chrome.zip
unzip chrome.zip -d .render/chrome
mv .render/chrome/chrome-linux64 .render/chrome/chrome
chmod +x .render/chrome/chrome/chrome

# Download Chromedriver
wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.60/linux64/chromedriver-linux64.zip -O chromedriver.zip
unzip chromedriver.zip -d .render/chromedriver
mv .render/chromedriver/chromedriver-linux64/chromedriver .render/chromedriver/chromedriver
chmod +x .render/chromedriver/chromedriver
apt update && apt install -y wget unzip
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb
python3 main.py

# Set executable paths
export PATH=$PATH:/opt/render/project/.render/chrome:/opt/render/project/.render/chromedriver
export CHROME_BIN="/opt/render/project/.render/chrome/chrome"
export CHROMEDRIVER_PATH="/opt/render/project/.render/chromedriver/chromedriver"
python3 main.py
# Run your app
python3 main.py
