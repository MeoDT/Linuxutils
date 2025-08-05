#!/bin/bash
set -e
d="$HOME/.venvmanager"
f="$d/venvm.py"
c="$d/venvm_config.json"
r="$d/.venvmanagerrc"
a="alias venvm='python3 $f'"
m() { p=$!; s="/-\|"; i=0; while kill -0 "$p" 2>/dev/null; do printf "\rInstalling %c" "${s:i++%${#s}:1}"; sleep 0.1; done; printf "\r"; }
mkdir -p "$d" >/dev/null 2>&1
( curl -sSLo "$f" https://raw.githubusercontent.com/MeoDT/Linuxutils/refs/heads/main/venvm.py && chmod +x "$f" && touch "$c" && { [ ! -f "$r" ] || ! grep -q "$a" "$r"; } && echo "$a" > "$r" ) & m
echo "✓ Installed and ready for use"
sleep 5
rm -- "$0"
