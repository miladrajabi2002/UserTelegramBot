#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════╗
# ║       UserBot Installer — Linux/macOS/WSL            ║
# ╚══════════════════════════════════════════════════════╝

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $1"; }
success() { echo -e "${GREEN}[OK]${RESET}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $1"; }
error()   { echo -e "${RED}[ERROR]${RESET} $1"; exit 1; }

echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
echo -e "${BOLD}   🤖  Personal Telegram UserBot Installer${RESET}"
echo -e "${BOLD}${CYAN}══════════════════════════════════════════${RESET}\n"

# ── 1. Check / Install Python 3.8+ ──────────────────────────────────────────

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        if "$cmd" -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
            PYTHON="$cmd"
            success "Python found: $($cmd --version)"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    warn "Python 3.8+ not found. Installing..."
    if command -v apt-get &>/dev/null; then
        apt-get update -qq
        apt-get install -y python3 python3-pip python3-venv python3-full
        PYTHON="python3"
    elif command -v brew &>/dev/null; then
        brew install python
        PYTHON="python3"
    elif command -v dnf &>/dev/null; then
        dnf install -y python3 python3-pip
        PYTHON="python3"
    elif command -v pacman &>/dev/null; then
        pacman -Sy --noconfirm python python-pip
        PYTHON="python3"
    else
        error "Python پیدا نشد. لطفاً از https://python.org نصب کنید."
    fi
    success "Python installed: $($PYTHON --version)"
fi

# ── 2. Install python3-venv if missing (Debian/Ubuntu) ──────────────────────
# Python 3.12+ on Debian/Ubuntu is "externally managed" — never use pip directly
# Always use a venv to avoid "externally-managed-environment" error (PEP 668)

if command -v apt-get &>/dev/null; then
    if ! $PYTHON -m venv --help &>/dev/null 2>&1; then
        info "Installing python3-venv & python3-full..."
        apt-get install -y python3-venv python3-full
        success "python3-venv installed"
    fi
fi

# ── 3. Create virtual environment ────────────────────────────────────────────

if [ ! -d "venv" ]; then
    info "Creating virtual environment (venv)..."
    $PYTHON -m venv venv
    success "Virtual environment created"
else
    success "Virtual environment already exists — skipping"
fi

# ── 4. Install packages inside venv ──────────────────────────────────────────

info "Installing required packages inside venv..."
./venv/bin/pip install --upgrade pip --quiet
./venv/bin/pip install telethon rich aiofiles --quiet

success "Packages installed:"
echo -e "   ${GREEN}•${RESET} telethon  $(./venv/bin/pip show telethon  2>/dev/null | grep Version | awk '{print $2}')"
echo -e "   ${GREEN}•${RESET} rich      $(./venv/bin/pip show rich      2>/dev/null | grep Version | awk '{print $2}')"
echo -e "   ${GREEN}•${RESET} aiofiles  $(./venv/bin/pip show aiofiles  2>/dev/null | grep Version | awk '{print $2}')"

# ── 5. Create saved_media folder ─────────────────────────────────────────────

mkdir -p saved_media
success "Created saved_media/ directory"

# ── 6. Create run.sh helper ──────────────────────────────────────────────────

cat > run.sh << 'EOF'
#!/usr/bin/env bash
# Helper: activates venv and runs the bot
cd "$(dirname "$0")"
source venv/bin/activate
exec python3 index.py
EOF
chmod +x run.sh
success "Created run.sh"

# ── 7. Done ──────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${GREEN}══════════════════════════════════════════${RESET}"
echo -e "${BOLD}  ✅  Installation complete!${RESET}"
echo -e "${BOLD}${GREEN}══════════════════════════════════════════${RESET}"
echo ""
echo -e "${BOLD}📋 مراحل بعدی:${RESET}"
echo -e "   ${CYAN}1.${RESET} API credentials از ${YELLOW}https://my.telegram.org${RESET} بگیر"
echo -e "   ${CYAN}2.${RESET} اجرا با: ${BOLD}${GREEN}./run.sh${RESET}"
echo ""
echo -e "${BOLD}📌 برای pm2 (همیشه روشن بمونه):${RESET}"
echo -e "   ${GREEN}pm2 start venv/bin/python3 --name userbot -- index.py${RESET}"
echo -e "   ${GREEN}pm2 save && pm2 startup${RESET}"
echo ""
