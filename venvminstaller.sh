#!/bin/bash
[ "$(uname)" != "Linux" ] && echo "✗ Linux only" && exit 1
set -e
d="$HOME/.venvmanager"; f="$d/venvm.py"; c="$d/venvm_config.json"; r="$d/.venvmanagerrc"; a="alias venvm='python3 $f'"
echo "✓ Created folders"
[ -d "$d" ] && rm -rf "$d"
echo "✓ Deleting old versions"
mkdir -p "$d" >/dev/null 2>&1
m() { p=$!; s="/-\|"; i=0; while kill -0 "$p" 2>/dev/null; do printf "\rInstalling %c" "${s:i++%4:1}"; sleep 0.1; done; printf "\r"; }
( curl -sSLo "$f" https://raw.githubusercontent.com/MeoDT/Linuxutils/refs/heads/main/venvm.py && chmod +x "$f" && touch "$c" && sed -i "/alias venvm=/d" "$r" 2>/dev/null || true && echo "$a" > "$r" ) & m
echo "✓ Installed and ready for use"
sleep 2
rm -- "$0"
