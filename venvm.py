import os
import sys
import json
import subprocess
from pathlib import Path

CONFIG_FILE = os.path.expanduser("~/.venvm_config.json")

class VenvManager:
    def __init__(self):
        self.venvs = self.load_config()
        self.cleanup_missing_venvs()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.venvs, f, indent=4)

    def cleanup_missing_venvs(self):
        to_delete = [name for name, path in self.venvs.items() if not os.path.exists(path)]
        for name in to_delete:
            del self.venvs[name]
        if to_delete:
            self.save_config()

    def generate_unique_name(self, base):
        name = base
        i = 1
        while name in self.venvs:
            name = f"{base}{i}"
            i += 1
        return name

    def create_venv(self, base_dir, name):
        full_path = os.path.join(base_dir, name)
        os.makedirs(full_path, exist_ok=True)
        subprocess.run(["python3", "-m", "venv", full_path])
        unique_name = self.generate_unique_name(name)
        self.venvs[unique_name] = full_path
        self.save_config()
        print(f"[OK] Virtual environment '{unique_name}' created at {full_path}")

    def delete_venv(self, name):
        if name not in self.venvs:
            print("[ERROR] Venv not found.")
            return
        path = self.venvs[name]
        subprocess.run(["rm", "-rf", path])
        del self.venvs[name]
        self.save_config()
        print(f"[OK] Deleted virtual environment '{name}'")

    def install_package(self, name, package):
        if name not in self.venvs:
            print("[ERROR] Venv not found.")
            return
        pip_path = os.path.join(self.venvs[name], "bin", "pip")
        subprocess.run([pip_path, "install", package])

    def run_pip_command(self, name, pip_args):
        if name not in self.venvs:
            print("[ERROR] Venv not found.")
            return
        pip_path = os.path.join(self.venvs[name], "bin", "pip")
        subprocess.run([pip_path] + pip_args)

    def list_help(self):
        print("""
venvmanager - Python venv manager by MeoDT software
Commands:
    venvm /path/to/venvs *name*
        - Creates a new virtual environment at the specified path with the given name.
    venvm cd *name*
        - Creates a virtual environment named *name* in the current directory.
    venvm *name* install *package*
        - Installs the specified package into the virtual environment.
    venvm *name* delete
        - Deletes the virtual environment.
    venvm *name* *any_pip_command*
        - Runs any pip command in the specified virtual environment.
    venvm help
        - Shows this help message.
""")

if __name__ == '__main__':
    args = sys.argv[1:]
    vm = VenvManager()

    if not args:
        print("[ERROR] No arguments provided.")
        vm.list_help()
        sys.exit(1)

    if args[0] == "help":
        vm.list_help()

    elif args[0] == "cd" and len(args) == 2:
        vm.create_venv(os.getcwd(), args[1])

    elif os.path.isabs(args[0]) and len(args) == 2:
        vm.create_venv(args[0], args[1])

    elif len(args) >= 2 and args[1] == "install":
        vm.install_package(args[0], args[2])

    elif len(args) == 2 and args[1] == "delete":
        vm.delete_venv(args[0])

    elif len(args) >= 2:
        vm.run_pip_command(args[0], args[1:])

    else:
        print("[ERROR] Invalid arguments.")
        vm.list_help()

    sys.exit(0)
