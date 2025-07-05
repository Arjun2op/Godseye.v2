#!/bin/bash

# Install system dependencies
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
    xdg-utils \
    google-chrome-stable

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Make sure the Chrome binary is in PATH
ln -s /usr/bin/google-chrome /usr/local/bin/chrome

# Run the application
python3 main.py
