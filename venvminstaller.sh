#!/bin/bash
set -e

USER_HOME="$HOME"
TARGET_DIR="$USER_HOME/.venvmanager"
ALIAS_FILE="$TARGET_DIR/.venvmanagerrc"
REPO_URL="https://raw.githubusercontent.com/MeoDT/Linuxutils/main/venvm.py"
SCRIPT_NAME="venvm.py"
BASHRC="$USER_HOME/.bashrc"
mkdir -p "$TARGET_DIR"
curl -fsSL "$REPO_URL" -o "$TARGET_DIR/$SCRIPT_NAME"
chmod +x "$TARGET_DIR/$SCRIPT_NAME"
echo "alias venvm='python3 $TARGET_DIR/$SCRIPT_NAME'" > "$ALIAS_FILE"
echo "[OK] Alias written to $ALIAS_FILE"
if ! grep -q "source $ALIAS_FILE" "$BASHRC"; then
    echo -e "\n# Load venvmanager aliases\nif [ -f \"$ALIAS_FILE\" ]; then\n    source \"$ALIAS_FILE\"\nfi" >> "$BASHRC"
    echo "[OK] Added source line to $BASHRC"
fi
source "$ALIAS_FILE"
#MeoDT software 2025

