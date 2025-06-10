# DatingBotPhishingSimulation

# Telegram Dating Bot 🤖❤️

A matchmaking bot that collects user profiles to find compatible partners based on personal details, interests, and location. It shows vulunerbilities could be exploited for hackers to harvest data 

## Features
- Multi-step profile registration
- Data validation (email, phone, birthdate)
- Social media integration
- Fake so-called notification system and wording to fool users that they will get notified for a match

## Setup Instructions

1. **Get Telegram Bot Token**:
   - Create a bot via [@BotFather](https://t.me/BotFather)
   - Copy your API token

2. **Configure Environment**:
   Replace placeholders in `Telegram dating bot.py`:
   ```python
   TOKEN = "YOUR_BOT_TOKEN_HERE"  # From BotFather
   OWNER_ID = "YOUR_TELEGRAM_ID"  # Get from @userinfobot
   OWNER_USERNAME = "YOUR_USERNAME"  # Without '@'
   ```
3. **Install Requirements**:
```bash
pip install python-telegram-bot
```
4. **Run the Bot**:
```bash
python "Telegram dating bot.py"
```
## Usage:

**Start bot** : /start

**Begin registration**: /register

**Cancel anytime**: /cancel

## Workflow:
**User provides personal details** (name, age, location)

**Shares professional info and interests**

**Adds social media profiles**

**Submits profile for matching**

## Note: All collected data is encrypted and only shared with potential matches upon user consent (well ,as it says lol :P).

## Security Notice:
🔒 Remove your real token before committing code
🔒 Keep OWNER_ID private in production

## Disclaimer : 
This is an ethical simulation made for Hong Kong PISA JAM 2025 by Kazel Lau on behalf of Hackertale , as the speaker for the workshop topic : "Most popular 2025 hacking tactics work in Telegram Bots: Ethical Simulation & Defense". We do not support any misuses and should those responsibilities be held accountable to respective users only but not the owner of this tool. 
