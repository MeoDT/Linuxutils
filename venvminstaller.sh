#!/bin/bash
[ "$(uname)" != "Linux" ]&&exit 1
set -e
if command -v pacman >/dev/null 2>&1;then sudo pacman -S --needed --noconfirm python python-pip curl
elif command -v apt >/dev/null 2>&1;then sudo apt update && sudo apt install -y python3 python3-pip curl
else echo Unsupported package manager; exit 1; fi
D="$HOME/.venvmanager";P="$D/venvm.py";F="$D/venvm_config.json";A="alias venvm='python3 $P'";RC="$HOME/.bashrc"
[[ $SHELL == *zsh* ]]&&RC="$HOME/.zshrc"
mkdir -p "$D"
[ -f "$P" ]&&rm -f "$P"
m(){ p=$!; s="/-\|"; i=0; while kill -0 "$p" 2>/dev/null; do printf "\rInstalling %c" "${s:i++%4:1}"; sleep .1; done; printf "\r"; }
(curl -sSLo "$P" "https://raw.githubusercontent.com/MeoDT/Linuxutils/refs/heads/main/venvm.py" && chmod +x "$P" && touch "$F") & m
grep -Fxq "$A" "$RC" 2>/dev/null || echo "$A" >> "$RC"
source "$RC"
echo Done.
rm -- "$0"
