

---

# venvmanager

**A simple, fast and user-friendly Python virtual environment manager for Linux.**

---

## Overview

`venvmanager` is a lightweight command-line tool to create, manage, install packages into, and delete Python virtual environments.
It keeps track of all your virtual environments with absolute paths stored in a JSON config file inside your home directory.
It supports unique naming, runs any pip commands in your venvs, and cleans up stale entries on startup.

---

## Features

* Create virtual environments in any directory or in the current working directory
* Install packages into specific virtual environments
* Run arbitrary pip commands inside a virtual environment
* Delete virtual environments safely
* Persistent storage of all managed venvs in `~/.venvmanager/venvm_config.json`
* Automatically removes missing venv entries on startup
* Unique naming with auto-increment on duplicates
* User-dynamic configuration and paths
* Simple CLI usage with helpful commands and feedback

---

## Installation

 Open your terminal and copy:
(Ubuntu based)
```markdown
cd ~/Desktop && wget -q https://raw.githubusercontent.com/MeoDT/Linuxutils/main/venvminstaller.sh -O venvminstaller.sh && chmod +x venvminstaller.sh && ./venvminstaller.sh
```
(Arch based)
```markdown
cd ~/Desktop && sudo pacman -S --needed --noconfirm python python-pip curl && wget -q https://raw.githubusercontent.com/MeoDT/Linuxutils/main/venvminstaller.sh -O venvminstaller.sh && chmod +x venvminstaller.sh && ./venvminstaller.sh
```
This script will:
   * Deletes old versions
   * Create the hidden directory `~/.venvmanager`
   * Download the `venvm.py` Python script into this folder
   * Set up a persistent alias `venvm` to run the tool easily
   * Deleting itself 

---
### Commands

| Command                                   | Description                                                    |
| ---------------------------------------- | -------------------------------------------------------------- |
| `venvm /path/to/venvs name`              | Create a new virtual environment at the specified path         |
| `venvm cd name`                          | Create a virtual environment named `name` in current directory |
| `venvm name install package`             | Install a Python package into the named virtual environment    |
| `venvm name install-multi pkg1 pkg2 ...` | Install multiple packages into the named virtual environment   |
| `venvm name delete`                      | Delete the named virtual environment                           |
| `venvm name <any_pip_command>`           | Run any pip command inside the named virtual environment       |
| `venvm list`                             | List all managed virtual environments                          |
| `venvm help`                             | Show help information                                          |

---
## Configuration

The tool stores all managed virtual environments in:

```
~/.venvmanager/venvm_config.json
```

This file is automatically created and maintained by the tool. No manual edits needed.

---

## Requirements

* Python 3 (with built-in `venv` module)
* Linux environment (tested on Linux Mint and Ubuntu)

---

## License

MIT License

---

## Author

MeoDT Software
Qsenja

---

## Notes

For any issues or feature requests, contact the author.

---
