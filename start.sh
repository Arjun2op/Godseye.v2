#!/bin/bash
# Start the Flask app
gunicorn main:app --bind 0.0.0.0:$PORT
