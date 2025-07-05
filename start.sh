#!/bin/bash

# Create directories
mkdir -p /opt/render/project/.render/chrome
mkdir -p /opt/render/project/.render/chromedriver

# Install dependencies
apt-get update && apt-get install -y \
    wget \
    unzip \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    libappindicator3-1 \
    xdg-utils

# Download and install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -yf
rm google-chrome-stable_current_amd64.deb

# Download ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}')
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}")
wget "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" -O chromedriver.zip
unzip chromedriver.zip -d /opt/render/project/.render/chromedriver
chmod +x /opt/render/project/.render/chromedriver/chromedriver
rm chromedriver.zip

# Set environment variables
export PATH=$PATH:/opt/render/project/.render/chromedriver
export CHROME_BIN="/usr/bin/google-chrome"
export CHROMEDRIVER_PATH="/opt/render/project/.render/chromedriver/chromedriver"

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
