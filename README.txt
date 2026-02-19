# SoccerProp Discord Alert Bot

A discord bot that monitors for new props from DFS and sends alerts to a Discord channel using a webhook.

## Features
- Logs in to SoccerProp
- Scrapes props for:
  - Passes Attempted
  - Clearances
  - Shots
- Sends Discord alerts when new props appear
- Waits until all 3 prop types have appeared at least once before sending any notifications (prevents early spam)

## Tech Stack
- Python
- Playwright (browser automation)
- Discord Webhook

## Setup
1) Install Python 3.x  
2) Install dependencies:
```bash
pip install -r requirements.txt
