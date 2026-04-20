# 🚀 Telegram UserBot

### 📌 Overview
A powerful and lightweight Telegram UserBot that allows you to:

- Download protected/private Telegram content
- Automatically save self-destructing media (TTL & View Once)
- Store files on your server
- Run safely using Python virtual environment (venv)

---

### 🛠 Commands

| Command | Description |
|--------|------------|
| `.help` | Show help menu |
| `.alive` | Show bot status, uptime, version |
| `.ping` | Check connection speed |
| `.stats` | Show statistics (files, size, uptime) |

---

### 📥 Download Content

| Command | Description |
|--------|------------|
| `.dl <link>` | Download from public channel |
| `.dl <private link>` | Download from private channel |
| `.dl (reply)` | Download replied message |

📌 Output will be sent to **Saved Messages**

---

### 📸 Auto Save (No Command Needed)

The bot automatically saves:

- Self-destructing media (TTL)
- View-once photos/videos

📌 All files are forwarded to **Saved Messages**

---

### 📂 Storage Path

```bash
~/bot/saved_media/
⚙️ Installation
git clone https://github.com/yourname/yourrepo
cd yourrepo
chmod +x install.sh && ./install.sh
./run.sh
🔧 Changes & Fixes
install.sh
Automatically installs python3-venv
Uses isolated environment (venv)
Prevents global pip issues
Creates run.sh for easy execution
index.py
Removed check_and_install_dependencies
Only checks required packages
📁 Project Structure
your-repo/
├── index.py
├── install.sh
├── run.sh
└── README.md
