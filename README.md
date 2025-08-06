

---

# venvmanager

**A simple, user-friendly Python virtual environment manager for Linux.**

---

## Overview

`venvmanager` is a lightweight command-line tool to create, manage, install packages into, and delete Python virtual environments.
It keeps track of all your virtual environments with absolute paths stored in a JSON config file inside your home directory.
It supports unique naming (with automatic numbering for duplicates), runs any pip commands in your venvs, and cleans up stale entries on startup.

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

1. Download the installer script `venvinstaller.sh`:

   ```bash
   wget https://raw.githubusercontent.com/MeoDT/Linuxutils/refs/heads/main/venvinstaller.sh
   ```

2. Make the script executable and set read/write permissions:

   ```bash
   chmod +x venvinstaller.sh
   chmod a+rw venvinstaller.sh
   ```

3. Run the installer script:

   ```bash
   ./venvinstaller.sh
   ```

   This script will:

   * Create the hidden directory `~/.venvmanager`
   * Download the `venvm.py` Python script into this folder
   * Set up a persistent alias `venvm` to run the tool easily
   * Open a terminal window and run `venvm help` to verify installation (with a short delay to ensure readiness)

---

## Usage

Run `venvm help` to see the full command list:

```bash
venvm help
```

### Commands

| Command                        | Description                                                    |
| ------------------------------ | -------------------------------------------------------------- |
| `venvm /path/to/venvs name`    | Create a new virtual environment at the specified path         |
| `venvm cd name`                | Create a virtual environment named `name` in current directory |
| `venvm name install package`   | Install a Python package into the named virtual environment    |
| `venvm name delete`            | Delete the named virtual environment                           |
| `venvm name <any_pip_command>` | Run any pip command inside the named virtual environment       |
| `venvm help`                   | Show help information                                          |

---

## Examples

Create venv in current directory:

```bash
venvm cd myenv
```

Create venv at custom path:

```bash
venvm /home/qsenja/projects venv1
```

Install package inside venv:

```bash
venvm venv1 install requests
```

Run arbitrary pip command:

```bash
venvm venv1 list
```

Delete venv:

```bash
venvm venv1 delete
```

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

For any issues or feature requests, please open an issue in the repository or contact the author.

---
