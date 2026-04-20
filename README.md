# 🤖 UserTelegramBot

A modern, personal Telegram userbot built with [Telethon](https://github.com/LonamiWebs/Telethon).

## ✨ Features

- 📸 **Auto-save** timed & view-once photos/videos → forwarded to Saved Messages
- 🔒 **Download protected content** from any channel link (`.dl`)
- 📊 **Management commands** — ping, stats, alive, help
- 🧱 **Modular & extensible** — easy to add new commands

---

## 🚀 Installation

> Supports: Ubuntu, Debian, and any Linux with `apt`

```bash
curl -fsSL https://raw.githubusercontent.com/miladrajabi2002/UserTelegramBot/main/install.sh | sudo bash
```

That's it. The installer will:
- Check / install Python 3
- Clone this repo to `/opt/userbot`
- Create a virtual environment
- Install all dependencies
- Add a global `userbot` command

---

## ▶️ Run

```bash
userbot
```

First run will ask for your **API ID**, **API Hash** (from [my.telegram.org](https://my.telegram.org)), and your phone number.

### Keep it running with pm2

```bash
pm2 start /opt/userbot/venv/bin/python3 --name userbot -- /opt/userbot/index.py
pm2 save && pm2 startup
```

---

## 📖 Commands

Send these as yourself in any Telegram chat:

| Command | Description |
|---------|-------------|
| `.help` | Show all commands |
| `.alive` | Bot status + uptime |
| `.ping` | Connection speed test |
| `.stats` | Saved files count & storage size |
| `.dl <link>` | Download protected content from a `t.me` link |
| `.dl` *(reply)* | Download the message you're replying to |

> All commands are **outgoing only** — only work when sent by you.

### Auto-save (no command needed)

Any **timed** or **view-once** media sent to you is automatically saved to `saved_media/` and forwarded to your Saved Messages.

---

## 📂 File Structure

```
/opt/userbot/
├── index.py          ← main bot
├── install.sh        ← installer
├── config.json       ← created on first run (API credentials)
├── my_userbot.session← Telegram session (created on first run)
├── saved_media/      ← all downloaded media
└── venv/             ← Python virtual environment
```

---

## ⚠️ Notes

- This is a **userbot** — it runs as your personal Telegram account
- Never share your `config.json` or `.session` file
- Use responsibly and follow [Telegram ToS](https://telegram.org/tos)
