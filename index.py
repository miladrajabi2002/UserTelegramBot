"""
╔══════════════════════════════════════════════════════════════╗
║              🤖 Personal Telegram UserBot                    ║
║              Built with Telethon (Latest)                    ║
║              Version: 2.0.0 | Python 3.8+                   ║
╚══════════════════════════════════════════════════════════════╝

Features:
  ✅ Auto-save timed/view-once photos & videos
  ✅ Download protected/copyright content via link
  ✅ Management commands (ping, stats, alive, etc.)
  ✅ Modular & extensible architecture
"""

import asyncio
import os
import sys
import re
import time
import logging
import platform
from datetime import datetime
from pathlib import Path

# ─── Dependency Check ──────────────────────────────────────────────────────────
# Packages are installed via install.sh inside a venv — no runtime pip needed.

def check_dependencies():
    missing = []
    for module in ("telethon", "rich", "aiofiles"):
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print("[HINT]  Run ./install.sh first, then start with ./run.sh")
        sys.exit(1)

check_dependencies()

# ─── Imports ──────────────────────────────────────────────────────────────────

from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
    DocumentAttributeVideo,
    MessageMediaWebPage,
)
from telethon.errors import FloodWaitError
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich import print as rprint
import aiofiles

# ─── Logger Setup ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler("userbot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("UserBot")
console = Console()

# ─── Config ────────────────────────────────────────────────────────────────────

SESSION_FILE   = "my_userbot"
SAVE_DIR       = Path("saved_media")
STATS_FILE     = Path("stats.json")
CONFIG_FILE    = Path("config.json")

# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_config() -> dict:
    import json
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(data: dict):
    import json
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_stats() -> dict:
    import json
    default = {"saved_media": 0, "downloaded": 0, "start_time": time.time()}
    if STATS_FILE.exists():
        with open(STATS_FILE, "r") as f:
            return {**default, **json.load(f)}
    return default

def save_stats(stats: dict):
    import json
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def uptime_str(start: float) -> str:
    delta = int(time.time() - start)
    h, rem = divmod(delta, 3600)
    m, s   = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def parse_tg_link(link: str):
    """Parse a t.me/channel/id or t.me/c/channel_id/msg_id link."""
    # Public: https://t.me/username/123
    m = re.match(r"https?://t\.me/([^/]+)/(\d+)", link)
    if m:
        return m.group(1), int(m.group(2))
    # Private: https://t.me/c/1234567890/123
    m = re.match(r"https?://t\.me/c/(\d+)/(\d+)", link)
    if m:
        return int(f"-100{m.group(1)}"), int(m.group(2))
    return None, None

async def smart_download(client, message, label="media") -> Path | None:
    """Download any media from a message and return its path."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        path = await client.download_media(message, file=str(SAVE_DIR / f"{label}_{ts}"))
        return Path(path) if path else None
    except Exception as e:
        log.error(f"Download error: {e}")
        return None

# ─── Setup Wizard ─────────────────────────────────────────────────────────────

def setup_wizard() -> dict:
    """Interactive first-run setup."""
    console.print(Panel(
        "[bold cyan]🤖 Personal Telegram UserBot[/bold cyan]\n"
        "[dim]Setup Wizard — First Run[/dim]",
        border_style="cyan"
    ))

    console.print("\n[yellow]📡 Get your API credentials from:[/yellow] [link=https://my.telegram.org]https://my.telegram.org[/link]\n")

    api_id  = Prompt.ask("[cyan]API ID[/cyan]").strip()
    api_hash = Prompt.ask("[cyan]API Hash[/cyan]").strip()

    cfg = {"api_id": int(api_id), "api_hash": api_hash}
    save_config(cfg)
    console.print("\n[green]✓ Config saved to config.json[/green]\n")
    return cfg

# ─── Bot Core ─────────────────────────────────────────────────────────────────

class UserBot:
    def __init__(self, cfg: dict):
        self.cfg    = cfg
        self.stats  = load_stats()
        self.client = TelegramClient(
            SESSION_FILE,
            cfg["api_id"],
            cfg["api_hash"],
            system_version="4.16.30-vxCUSTOM",   # mimic official client
        )
        self._me = None

    # ── Startup ────────────────────────────────────────────────────────────────

    async def start(self):
        await self.client.start()
        self._me = await self.client.get_me()
        self.stats["start_time"] = self.stats.get("start_time", time.time())

        console.print(Panel(
            f"[bold green]✅ UserBot Started![/bold green]\n"
            f"[white]👤 Account :[/white] [cyan]{self._me.first_name}[/cyan]"
            f"{'  @' + self._me.username if self._me.username else ''}\n"
            f"[white]🆔 User ID  :[/white] [cyan]{self._me.id}[/cyan]\n"
            f"[white]📂 Save dir :[/white] [cyan]{SAVE_DIR.resolve()}[/cyan]\n"
            f"[white]⏰ Started  :[/white] [cyan]{datetime.now().strftime('%H:%M:%S')}[/cyan]",
            title="[bold]UserBot[/bold]",
            border_style="green"
        ))

        self._register_handlers()
        console.print("[dim]Listening for events... (Ctrl+C to stop)[/dim]\n")
        await self.client.run_until_disconnected()

    # ── Handlers Registration ──────────────────────────────────────────────────

    def _register_handlers(self):
        client = self.client

        # ── 1. Auto-save timed/view-once media ──────────────────────────────────
        @client.on(events.NewMessage(incoming=True))
        async def on_incoming(event):
            msg = event.message
            if not msg.media:
                return

            is_timed    = getattr(msg, "ttl_seconds", None)
            is_view_once = False

            # Detect view-once (noforwards flag or Document attribute)
            if hasattr(msg, "noforwards") and msg.noforwards:
                is_view_once = True
            if isinstance(msg.media, MessageMediaDocument):
                doc = msg.media.document
                for attr in doc.attributes:
                    if hasattr(attr, "round_message") or hasattr(attr, "voice"):
                        pass
                # Telethon exposes ttl_seconds on the message itself for view-once
            if is_timed or is_view_once or getattr(msg.media, "ttl_seconds", None):
                await self._handle_timed_media(msg)

        # ── 2. Protected content downloader (.dl command in Saved Messages) ──────
        @client.on(events.NewMessage(
            outgoing=True,
            pattern=r"\.dl(?:\s+(.+))?",
        ))
        async def on_dl(event):
            await event.delete()
            match  = event.pattern_match.group(1)
            link   = match.strip() if match else None

            # If replying to a message, download that
            if event.is_reply:
                replied = await event.get_reply_message()
                await self._download_and_forward(event, replied)
                return

            if link:
                channel, msg_id = parse_tg_link(link)
                if not channel:
                    await self._send_status(event, "❌ لینک نامعتبر است.")
                    return
                await self._download_by_link(event, channel, msg_id)
            else:
                await self._send_status(event, "⚠️ استفاده: `.dl <link>` یا reply روی پیام")

        # ── 3. Management Commands ────────────────────────────────────────────────
        @client.on(events.NewMessage(outgoing=True, pattern=r"\.ping$"))
        async def on_ping(event):
            start = time.perf_counter()
            await event.edit("🏓 Pinging...")
            ms = (time.perf_counter() - start) * 1000
            await event.edit(f"🏓 **Pong!** `{ms:.1f}ms`")

        @client.on(events.NewMessage(outgoing=True, pattern=r"\.alive$"))
        async def on_alive(event):
            up = uptime_str(self.stats["start_time"])
            ver = sys.version.split()[0]
            txt = (
                f"🤖 **UserBot is alive!**\n\n"
                f"⏱ Uptime  : `{up}`\n"
                f"🐍 Python  : `{ver}`\n"
                f"📦 Telethon: `{self._telethon_version()}`\n"
                f"💾 Saved   : `{self.stats['saved_media']}` files\n"
                f"📥 Fetched : `{self.stats['downloaded']}` protected items"
            )
            await event.edit(txt)

        @client.on(events.NewMessage(outgoing=True, pattern=r"\.stats$"))
        async def on_stats(event):
            up = uptime_str(self.stats["start_time"])
            saved_size = sum(f.stat().st_size for f in SAVE_DIR.rglob("*") if f.is_file()) if SAVE_DIR.exists() else 0
            size_mb = saved_size / (1024 * 1024)
            txt = (
                f"📊 **UserBot Stats**\n\n"
                f"⏱ Uptime        : `{up}`\n"
                f"📸 Timed media   : `{self.stats['saved_media']}`\n"
                f"🔒 Protected DL  : `{self.stats['downloaded']}`\n"
                f"💽 Storage used  : `{size_mb:.2f} MB`\n"
                f"📂 Save folder   : `{SAVE_DIR.resolve()}`"
            )
            await event.edit(txt)

        @client.on(events.NewMessage(outgoing=True, pattern=r"\.help$"))
        async def on_help(event):
            txt = (
                "📖 **UserBot Commands**\n\n"
                "**Media**\n"
                "• Auto-saves all timed/once-view media\n"
                "• `.dl <link>` — دانلود محتوای protected از لینک\n"
                "• `.dl` (reply) — دانلود همان پیام\n\n"
                "**Management**\n"
                "• `.ping` — تست سرعت\n"
                "• `.alive` — وضعیت ربات\n"
                "• `.stats` — آمار کامل\n"
                "• `.help` — همین پیام\n\n"
                "**💡 تیپ:** همه دستورات فقط در چت‌های شما کار می‌کنن (outgoing)"
            )
            await event.edit(txt)

    # ── Feature: Timed / View-Once Media ──────────────────────────────────────

    async def _handle_timed_media(self, msg):
        """Download timed or view-once media, save it, then forward to Saved Messages."""
        try:
            path = await smart_download(self.client, msg, label="timed")
            if not path:
                return

            log.info(f"Saved timed media: {path}")
            self.stats["saved_media"] += 1
            save_stats(self.stats)

            sender = await msg.get_sender()
            sender_name = getattr(sender, "first_name", "Unknown") if sender else "Unknown"
            caption = (
                f"📸 **Auto-saved media**\n"
                f"👤 From  : {sender_name}\n"
                f"🕐 Time  : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"📁 File  : `{path.name}`"
            )

            await self.client.send_file(
                "me",
                str(path),
                caption=caption,
                force_document=False,
            )
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            log.error(f"Timed media handler error: {e}")

    # ── Feature: Protected Content Downloader ─────────────────────────────────

    async def _download_by_link(self, event, channel, msg_id: int):
        """Fetch a message by link and send its content to Saved Messages."""
        status = await self.client.send_message("me", f"⏳ در حال دریافت پیام...")
        try:
            target_msg = await self.client.get_messages(channel, ids=msg_id)
            if not target_msg:
                await status.edit("❌ پیام پیدا نشد یا دسترسی ندارید.")
                return
            await self._deliver_content(status, target_msg, channel, msg_id)
        except Exception as e:
            await status.edit(f"❌ خطا: `{e}`")
            log.error(f"Download by link error: {e}")

    async def _download_and_forward(self, event, replied_msg):
        """Download and forward a replied-to message."""
        status = await self.client.send_message("me", "⏳ در حال دریافت...")
        try:
            await self._deliver_content(status, replied_msg)
        except Exception as e:
            await status.edit(f"❌ خطا: `{e}`")

    async def _deliver_content(self, status_msg, src_msg, channel=None, msg_id=None):
        """Core: download media/text from src_msg and send to Saved Messages."""
        self.stats["downloaded"] += 1
        save_stats(self.stats)

        ref = f"[{channel}/{msg_id}]" if channel else "[reply]"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        # ── Has media ────────────────────────────────────────────────────────────
        if src_msg.media:
            path = await smart_download(self.client, src_msg, label="protected")
            if path:
                caption_parts = [f"🔒 **Protected content saved** {ref}", f"🕐 {timestamp}"]
                if src_msg.text:
                    caption_parts.append(f"\n📝 {src_msg.text[:200]}")

                await self.client.send_file(
                    "me",
                    str(path),
                    caption="\n".join(caption_parts),
                    force_document=False,
                )
                await status_msg.edit(f"✅ ذخیره شد: `{path.name}`")
                return

        # ── Text only ────────────────────────────────────────────────────────────
        if src_msg.text:
            txt = f"📋 **Saved text** {ref}\n🕐 {timestamp}\n\n{src_msg.text}"
            await self.client.send_message("me", txt)
            await status_msg.edit("✅ متن ذخیره شد.")
            return

        await status_msg.edit("⚠️ محتوایی برای ذخیره پیدا نشد.")

    # ── Helpers ────────────────────────────────────────────────────────────────

    async def _send_status(self, event, text: str):
        await self.client.send_message("me", text)

    def _telethon_version(self) -> str:
        try:
            import telethon
            return telethon.__version__
        except Exception:
            return "unknown"


# ─── Entry Point ──────────────────────────────────────────────────────────────

async def main():
    cfg = load_config()
    if not cfg.get("api_id") or not cfg.get("api_hash"):
        cfg = setup_wizard()

    bot = UserBot(cfg)
    try:
        await bot.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Stopped by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ Fatal error: {e}[/red]")
        log.exception("Fatal error")

if __name__ == "__main__":
    asyncio.run(main())
