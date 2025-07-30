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

## Option 1: Manual Session Cookies (Recommended)

Most Pathfinder instances require manual session cookies. Create a .env file with:

```
MAP_ID=1
PF_SESSION=your_pathfinder_session_cookie
PF_CHAR_COOKIE=your_pf_char_cookie_value
PF_CHARACTER=your_pathfinder_character_id
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```

To get your session cookies, run:

```bash
python3 get_session_cookies.py
```

This will guide you through getting the required cookies from your browser.

## Option 2: EVE SSO Authentication (Experimental)

Some Pathfinder instances may support EVE SSO. Create a .env file with:

```
MAP_ID=1
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
EVE_CLIENT_ID=your_eve_client_id
EVE_CLIENT_SECRET=your_eve_client_secret
EVE_CALLBACK_URL=http://localhost:8080/callback
PATHFINDER_URL=https://path.shadowflight.org
```

Then run the setup script:

```bash
python3 setup_auth.py
```

**Note:** EVE SSO with Pathfinder is experimental and may not work with all Pathfinder instances.

# Running it

## First Time Setup

### Option 1: Manual Session Cookies (Recommended)

1. **Get your Pathfinder session cookies:**
   ```bash
   python3 get_session_cookies.py
   ```

2. **Set up your .env file** with the cookie values

3. **Start the bot:**
   ```bash
   python3 -m main
   ```

### Option 2: EVE SSO Authentication (Experimental)

1. **Get EVE Developer Credentials:**
   - Go to https://developers.eveonline.com/
   - Create a new application
   - Set callback URL to: `http://localhost:8080/callback`
   - Copy the Client ID and Client Secret

2. **Set up your .env file** (see Environment Setup above)

3. **Run the authentication setup:**
   ```bash
   python3 setup_auth.py
   ```

4. **Start the bot:**
   ```bash
   python3 -m main
   ```

## Subsequent Runs

Once set up, you can simply run:

```bash
python3 -m main
```

The bot will automatically use the best available authentication method.

# 🧭 How It Works

### Fetch Map Data

The bot pulls system and connection info from your Pathfinder instance using the updateData endpoint.

### Build Graph

Systems and their connections are stored in a bidirectional graph using Python's defaultdict(list).

### Detect Changes

If connections change (new or removed), those changes are logged and persisted.

### Find Path to High-Sec

It uses breadth-first search (BFS) to look for any route from your defined home system to a high-sec system using only system names.

### Send Alerts

When a new path is found, or connections are updated, the bot sends an alert via Discord and logs it locally.

# Future work

ask in Discord for a route from the wormhole out to high sec