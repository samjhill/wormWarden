# 🚙 Pathfinder Wormhole Alert Bot

This is a lightweight Python bot that watches your [Pathfinder](https://github.com/exodus4d/pathfinder) wormhole map for connection changes and sends real-time alerts to a Discord channel.

## 🔍 Features

* ✅ **Tracks all wormhole connections** on your Pathfinder map
* 📮 **Alerts on new or removed connections** via Discord
* 🗜 **Fetches system data automatically** using Pathfinder’s `updateData` API
* 🧠 **Caches connection state** to detect changes over time
* 📝 Logs all events to a local file for auditing

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` File

Create a `.env` file in the root folder and paste:

```dotenv
PF_SESSION=your_pathfinder_session_cookie
PF_CHAR_COOKIE=your_pf_character_cookie
PF_CHARACTER=your_character_id
MAP_ID=1  # your Pathfinder map ID
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
```

To get these values:

* Open Pathfinder in Chrome
* Open DevTools → Network → Inspect `updateData` or `System` requests
* Copy values from `Cookie` and `pf-character` headers

### 4. Run the Bot

```bash
python wh_alert_bot.py
```

You’ll see logs like:

```
🚀 Pathfinder WH Alert Bot running...
connection from J142754 to J103120
➕ New connection: J142754 → J103120
```

---

## 🔪 How It Works

1. Pulls system and connection data using `api/Map/updateData`
2. Converts that to a list of `(source, target)` wormhole connections
3. Tracks previous connections in memory and diffs each cycle
4. Sends Discord alerts for:

   * New connections (`➕`)
   * Removed/collapsed connections (`❌`)
5. Logs every change to `wh_alerts.log`

---

## 💡 Planned Features (optional)

* Alert on **signature-level changes** (e.g. mass, EOL)
* Chain-specific filters or whitelisting
* Slack / email / SMS integration
* Web dashboard showing current connection graph

---

## 🛠 Troubleshooting

* **403/401 Errors** → Your Pathfinder session cookie likely expired. Refresh cookies.
* **500 Errors on `/map/{id}/data`** → Use `updateData` instead (already handled in this script).
* **No alerts showing up?** → Check if Pathfinder is updating your map properly and that systems are linked.

---

## ✨ Credits

* Powered by [Pathfinder](https://github.com/exodus4d/pathfinder)
* EVE Online © CCP Games
