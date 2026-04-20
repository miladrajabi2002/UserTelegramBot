#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════╗
# ║   🤖 UserTelegramBot — One-Command Installer         ║
# ║   https://github.com/miladrajabi2002/UserTelegramBot ║
# ╚══════════════════════════════════════════════════════╝
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/miladrajabi2002/UserTelegramBot/main/install.sh | sudo bash

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $1"; }
success() { echo -e "${GREEN}[✓]${RESET}    $1"; }
warn()    { echo -e "${YELLOW}[!]${RESET}    $1"; }
error()   { echo -e "${RED}[✗]${RESET}    $1"; exit 1; }

REPO_URL="https://github.com/miladrajabi2002/UserTelegramBot.git"
INSTALL_DIR="$(pwd)/UserTelegramBot"

echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════════${RESET}"
echo -e "${BOLD}   🤖  UserTelegramBot — Installer              ${RESET}"
echo -e "${BOLD}${CYAN}══════════════════════════════════════════════${RESET}\n"

# ── 1. Root check ────────────────────────────────────────────────────────────

if [ "$EUID" -ne 0 ]; then
    error "Please run with sudo:\n   curl -fsSL ... | sudo bash"
fi

# ── 2. Install system dependencies ──────────────────────────────────────────

info "Updating package list..."
apt-get update -qq

info "Installing system packages..."
apt-get install -y \
    python3 \
    python3-venv \
    python3-full \
    git \
    curl \
    --no-install-recommends -qq

success "System packages ready"

# ── 3. Verify Python version ─────────────────────────────────────────────────

PYTHON=$(command -v python3 || command -v python)
[ -z "$PYTHON" ] && error "Python not found after install!"

PY_VER=$($PYTHON --version 2>&1)
$PYTHON -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" \
    || error "Python 3.8+ required. Found: $PY_VER"

success "Python: $PY_VER"

# ── 4. Clone / update repo ───────────────────────────────────────────────────

if [ -d "$INSTALL_DIR/.git" ]; then
    info "Updating existing installation at $INSTALL_DIR ..."
    git -C "$INSTALL_DIR" pull --quiet
    success "Repository updated"
else
    info "Cloning repository to $INSTALL_DIR ..."
    git clone --quiet "$REPO_URL" "$INSTALL_DIR"
    success "Repository cloned"
fi

cd "$INSTALL_DIR"

# ── 5. Create virtual environment ────────────────────────────────────────────

if [ ! -d "venv" ]; then
    info "Creating virtual environment..."
    $PYTHON -m venv venv
    success "Virtual environment created"
else
    success "Virtual environment already exists"
fi

# ── 6. Install Python packages inside venv ───────────────────────────────────
# Never use system pip directly — Python 3.12+ on Debian is externally managed

info "Installing Python packages..."
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip --quiet
"$INSTALL_DIR/venv/bin/pip" install telethon rich aiofiles --quiet

success "Packages installed:"
for pkg in telethon rich aiofiles; do
    VER=$("$INSTALL_DIR/venv/bin/pip" show "$pkg" 2>/dev/null | grep Version | awk '{print $2}')
    echo -e "   ${GREEN}•${RESET} $pkg $VER"
done

# ── 7. Create saved_media folder ─────────────────────────────────────────────

mkdir -p "$INSTALL_DIR/saved_media"
success "Created saved_media/ directory"

# ── 8. Create global launch command ──────────────────────────────────────────

cat > /usr/local/bin/UserTelegramBot << EOF
#!/usr/bin/env bash
cd $INSTALL_DIR
exec $INSTALL_DIR/venv/bin/python3 index.py "\$@"
EOF
chmod +x /usr/local/bin/UserTelegramBot
success "Global command created: UserTelegramBot"

# ── 9. Done ──────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  ✅  Installation complete!${RESET}"
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════${RESET}"
echo ""
echo -e "${BOLD}📂 Installed to:${RESET} ${CYAN}$INSTALL_DIR${RESET}"
echo ""
echo -e "${BOLD}📋 Next steps:${RESET}"
echo -e "   ${CYAN}1.${RESET} Get your API credentials from ${YELLOW}https://my.telegram.org${RESET}"
echo -e "   ${CYAN}2.${RESET} Start the bot:"
echo -e "      ${BOLD}${GREEN}UserTelegramBot${RESET}"
echo ""
echo -e "${BOLD}📌 Keep it running with pm2:${RESET}"
echo -e "   ${GREEN}pm2 start $INSTALL_DIR/venv/bin/python3 --name UserTelegramBot -- $INSTALL_DIR/index.py${RESET}"
echo -e "   ${GREEN}pm2 save && pm2 startup${RESET}"
echo ""
