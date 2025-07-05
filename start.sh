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
    libgtk-3-0

# Download Chrome
wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.60/linux64/chrome-linux64.zip -O chrome.zip
unzip chrome.zip -d /opt/render/project/.render/chrome
mv /opt/render/project/.render/chrome/chrome-linux64/chrome /opt/render/project/.render/chrome/
chmod +x /opt/render/project/.render/chrome/chrome

# Download Chromedriver
wget https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.60/linux64/chromedriver-linux64.zip -O chromedriver.zip
unzip chromedriver.zip -d /opt/render/project/.render/chromedriver
mv /opt/render/project/.render/chromedriver/chromedriver-linux64/chromedriver /opt/render/project/.render/chromedriver/
chmod +x /opt/render/project/.render/chromedriver/chromedriver

# Clean up
rm chrome.zip chromedriver.zip

# Set environment variables
export PATH=$PATH:/opt/render/project/.render/chrome:/opt/render/project/.render/chromedriver
export CHROME_BIN="/opt/render/project/.render/chrome/chrome"
export CHROMEDRIVER_PATH="/opt/render/project/.render/chromedriver/chromedriver"

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python3 main.py
