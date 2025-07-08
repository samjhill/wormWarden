# Pathfinder Wormhole Alert Bot 🚀

This Python bot monitors your [Pathfinder](https://github.com/exodus4d/pathfinder) wormhole mapping instance for changes in wormhole connections and alerts when a path is discovered from your home system (e.g., `J103453`) to high-sec space.

## ✨ Features

- 🔄 Fetches system and connection data from Pathfinder
- 📈 Builds and prints a wormhole connection graph
- 🧠 Tracks graph changes across runs
- 📍 Alerts when a path from your home system to high-sec is found (even across multiple hops!)
- 💬 Sends alerts to a Discord webhook
- 🪢 Handles broken connections and reconnections
- 💾 Saves connection state to disk for persistence

---

## 🧰 Requirements

- Python 3.8+
- A running Pathfinder instance
- `.env` file with your session and character info
- A Discord webhook URL

Install dependencies:

```bash
pip install -r requirements.txt
```


# 🛠️ Environment Setup

Create a .env file with the following keys:

```
MAP_ID=1
PF_SESSION=your_pathfinder_session_cookie
PF_CHAR_COOKIE=your_pf_char_cookie_value
PF_CHARACTER=your_pathfinder_character_id
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```