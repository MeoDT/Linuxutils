#!/bin/bash
[ "$(uname)" != "Linux" ] && exit 1
set -e
if command -v pacman >/dev/null 2>&1; then sudo pacman -S --needed --noconfirm python python-pip curl
elif command -v apt >/dev/null 2>&1; then sudo apt update && sudo apt install -y python3 python3-pip curl
else echo "Unsupported pkg mgr"; exit 1; fi
D="$HOME/.venvmanager"; F="$D/venvm_config.json"; P="$D/venvm.py"; A="alias venvm='python3 $P'"; RC="$HOME/.bashrc"
[[ $SHELL == *zsh* ]] && RC="$HOME/.zshrc"
[ -d "$D" ] && rm -rf "$D"
mkdir -p "$D"
m(){ p=$!; s="/-\|"; i=0; while kill -0 "$p" 2>/dev/null; do printf "\rInstalling %c" "${s:i++%4:1}"; sleep 0.1; done; printf "\r"; }
( curl -sSLo "$P" "https://raw.githubusercontent.com/MeoDT/Linuxutils/refs/heads/main/venvm.py" && chmod +x "$P" && touch "$F" ) & m
grep -Fxq "$A" "$RC" 2>/dev/null || echo "$A" >> "$RC"
echo "Done. Run 'source $RC' or reopen terminal."
