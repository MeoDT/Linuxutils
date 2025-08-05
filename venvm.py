#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import threading
import time
import multiprocessing
import platform
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Linux-only check
if platform.system() != "Linux":
    print("✗ This program is designed for Linux only")
    sys.exit(1)

CONFIG_DIR = os.path.expanduser("~/.venvmanager")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(CONFIG_DIR, "venvm_config.json")
SCRIPT_PATH = os.path.realpath(__file__)

class Spinner:
    def __init__(self, message="Working"):
        self.message = message
        self.spinning = False
        self.thread = None
        self.start_time = None
        self.chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def start(self):
        self.spinning = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._spin, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.spinning = False
        if self.thread:
            self.thread.join(timeout=0.1)
        print("\r" + " " * 60, end="\r", flush=True)
    
    def _spin(self):
        i = 0
        while self.spinning:
            elapsed = time.time() - self.start_time
            char = self.chars[i % len(self.chars)]
            print(f"\r{char} {self.message} [{elapsed:.1f}s]", end="", flush=True)
            time.sleep(0.08)
            i += 1

class VenvManager:
    def __init__(self):
        self.max_workers = multiprocessing.cpu_count() * 2
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Ensure cache dir exists
        os.makedirs(os.path.expanduser("~/.cache/pip"), exist_ok=True)
        
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'w') as f:
                json.dump({}, f)
        
        self.venvs = self._load_config()
        self._cleanup_missing()

    def _load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.venvs, f, indent=2)

    def _cleanup_missing(self):
        missing = [name for name, path in self.venvs.items() 
                  if subprocess.run(["test", "-d", path], capture_output=True).returncode != 0]
        for name in missing:
            del self.venvs[name]
        if missing:
            self._save_config()

    def _unique_name(self, base):
        name, i = base, 1
        while name in self.venvs:
            name = f"{base}{i}"
            i += 1
        return name

    def _get_fast_env(self):
        env = os.environ.copy()
        env.update({
            'PYTHONDONTWRITEBYTECODE': '1',
            'PYTHONUNBUFFERED': '1',
            'PIP_CACHE_DIR': os.path.expanduser("~/.cache/pip"),
            'PIP_NO_WARN_SCRIPT_LOCATION': '1',
            'PIP_DISABLE_PIP_VERSION_CHECK': '1',
            'PIP_NO_COLOR': '1',
            'PIP_QUIET': '2',
            'PIP_PREFER_BINARY': '1',
            'TMPDIR': '/tmp',
        })
        return env

    def _silent_run(self, cmd, env=None):
        return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                            stdin=subprocess.DEVNULL, env=env or self._get_fast_env())

    def _create_venv_task(self, base_dir, name):
        full_path = os.path.join(base_dir, name)
        unique_name = self._unique_name(name)
        env = self._get_fast_env()
        
        try:
            # Create venv
            result = self._silent_run([sys.executable, "-m", "venv", "--without-pip", "--clear", full_path], env)
            if result.returncode != 0:
                return {"success": False, "error": "venv creation failed"}
            
            # Install pip
            pip_result = self._silent_run([os.path.join(full_path, "bin", "python"), 
                                         "-m", "ensurepip", "--upgrade", "--default-pip"], env)
            
            self.venvs[unique_name] = os.path.abspath(full_path)
            self._save_config()
            return {"success": True, "name": unique_name, "path": full_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _delete_venv_task(self, name, path):
        try:
            if subprocess.run(["test", "-d", path], capture_output=True).returncode == 0:
                result = self._silent_run(["rm", "-rf", path])
                if result.returncode != 0:
                    shutil.rmtree(path, ignore_errors=True)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _install_package_task(self, pip_path, package):
        try:
            env = self._get_fast_env()
            cmd = [pip_path, "install", "--upgrade", "--prefer-binary", 
                  "--no-warn-script-location", "--disable-pip-version-check", package]
            
            result = self._silent_run(cmd, env)
            if result.returncode != 0:
                return {"success": False, "package": package}
            return {"success": True, "package": package}
        except Exception:
            return {"success": False, "package": package}

    def _batch_install_task(self, pip_path, packages):
        try:
            env = self._get_fast_env()
            cmd = [pip_path, "install", "--upgrade", "--prefer-binary", 
                  "--no-warn-script-location", "--disable-pip-version-check"] + packages
            
            result = self._silent_run(cmd, env)
            return result.returncode == 0
        except Exception:
            return False

    def create_venv(self, base_dir, name):
        full_path = os.path.join(base_dir, name)
        
        # Quick check if directory already exists
        if os.path.exists(full_path):
            print(f"✗ Directory '{name}' already exists at {full_path}")
            return
        
        spinner = Spinner(f"Creating venv '{name}'")
        spinner.start()
        
        future = self.executor.submit(self._create_venv_task, base_dir, name)
        result = future.result()
        
        spinner.stop()
        if result["success"]:
            print(f"✓ Created '{result['name']}'")
        else:
            print("✗ Failed to create venv")

    def delete_venv(self, name):
        if name not in self.venvs:
            print("✗ Venv not found")
            return
        
        spinner = Spinner(f"Deleting '{name}'")
        spinner.start()
        
        future = self.executor.submit(self._delete_venv_task, name, self.venvs[name])
        result = future.result()
        
        spinner.stop()
        if result["success"]:
            del self.venvs[name]
            self._save_config()
            print(f"✓ Deleted '{name}'")
        else:
            print("✗ Failed to delete venv")

    def install_package(self, name, package):
        if name not in self.venvs:
            print("✗ Venv not found")
            return
        
        # Quick check if venv still exists
        venv_path = self.venvs[name]
        if not os.path.exists(venv_path):
            print(f"✗ Venv '{name}' directory missing")
            return
        
        spinner = Spinner(f"Installing {package}")
        spinner.start()
        
        pip_path = os.path.join(venv_path, "bin", "pip")
        future = self.executor.submit(self._install_package_task, pip_path, package)
        result = future.result()
        
        spinner.stop()
        if result["success"]:
            print(f"✓ Installed {package}")
        else:
            print(f"✗ Failed to install {package}")

    def install_multiple(self, name, packages):
        if name not in self.venvs:
            print("✗ Venv not found")
            return
        
        # Quick check if venv still exists
        venv_path = self.venvs[name]
        if not os.path.exists(venv_path):
            print(f"✗ Venv '{name}' directory missing")
            return
        
        pip_path = os.path.join(venv_path, "bin", "pip")
        spinner = Spinner(f"Installing {len(packages)} packages")
        spinner.start()
        
        # Try batch install first
        batch_future = self.executor.submit(self._batch_install_task, pip_path, packages)
        batch_success = batch_future.result()
        
        if batch_success:
            spinner.stop()
            print(f"✓ Installed all {len(packages)} packages")
            return
        
        # Fall back to individual installs
        futures = [self.executor.submit(self._install_package_task, pip_path, pkg) for pkg in packages]
        results = [f.result() for f in futures]
        
        spinner.stop()
        successful = sum(1 for r in results if r["success"])
        
        if successful == len(packages):
            print(f"✓ Installed all {len(packages)} packages")
        elif successful > 0:
            print(f"✓ Installed {successful}/{len(packages)} packages")
        else:
            print("✗ Failed to install packages")

    def run_pip_command(self, name, args):
        if name not in self.venvs:
            print("✗ Venv not found")
            return
        
        # Quick check if venv still exists
        venv_path = self.venvs[name]
        if not os.path.exists(venv_path):
            print(f"✗ Venv '{name}' directory missing")
            return
        
        spinner = Spinner(f"Running pip {' '.join(args)}")
        spinner.start()
        
        pip_path = os.path.join(venv_path, "bin", "pip")
        try:
            result = subprocess.run([pip_path] + args, capture_output=True, text=True, env=self._get_fast_env())
            spinner.stop()
            
            if result.returncode == 0:
                print("✓ Command completed")
                if result.stdout.strip() and len(result.stdout.split('\n')) <= 5:
                    print(result.stdout.strip())
            else:
                print("✗ Command failed")
        except Exception:
            spinner.stop()
            print("✗ Error occurred")

    def list_venvs(self):
        if not self.venvs:
            print("No virtual environments found")
            return
        
        print("Virtual environments:")
        for name, path in self.venvs.items():
            status = "✓" if subprocess.run(["test", "-d", path], capture_output=True).returncode == 0 else "✗"
            try:
                size_result = subprocess.run(["du", "-sh", path], capture_output=True, text=True)
                size = size_result.stdout.split()[0] if size_result.returncode == 0 else "N/A"
            except:
                size = "N/A"
            print(f"  {status} {name:<15} {size:<8} {path}")

    def show_help(self):
        print(f"""venvm - Linux venv manager ({self.max_workers} threads)

Usage:
  venvm /path/to/dir <name>     Create venv at path
  venvm cd <name>               Create venv in current dir
  venvm <name> install <pkg>    Install package  
  venvm <name> install-multi <pkg1> <pkg2>...  Install multiple packages
  venvm <name> delete           Delete venv
  venvm <name> <pip_args>       Run pip command
  venvm list                    List all venvs
  venvm help                    Show this help

Config: {CONFIG_DIR}
""")

    def cleanup(self):
        self.executor.shutdown(wait=True)

def main():
    args = sys.argv[1:]
    vm = VenvManager()
    
    try:
        if not args or args[0] == "help":
            vm.show_help()
        elif args[0] == "list":
            vm.list_venvs()
        elif args[0] == "cd" and len(args) == 2:
            vm.create_venv(os.getcwd(), args[1])
        elif len(args) == 2 and os.path.isabs(args[0]):
            vm.create_venv(args[0], args[1])
        elif len(args) == 3 and args[1] == "install":
            vm.install_package(args[0], args[2])
        elif len(args) >= 3 and args[1] == "install-multi":
            vm.install_multiple(args[0], args[2:])
        elif len(args) == 2 and args[1] == "delete":
            vm.delete_venv(args[0])
        elif len(args) >= 2:
            vm.run_pip_command(args[0], args[1:])
        else:
            print("✗ Invalid arguments")
            vm.show_help()
    finally:
        vm.cleanup()

if __name__ == '__main__':
    main()
