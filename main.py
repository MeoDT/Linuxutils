import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import json
from pathlib import Path

class FastVenvManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Venv Mini Manager")
        self.root.geometry("550x400")
        self.root.configure(bg='#000000')
        
        # Setup wolkig schwarz style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#111111', foreground='#CCCCCC')
        self.style.configure('TFrame', background='#111111')
        self.style.configure('TNotebook', background='#222222')
        self.style.configure('TNotebook.Tab', 
                            background='#222222', 
                            foreground='#CCCCCC',
                            padding=(10, 4))
        self.style.map('TNotebook.Tab', 
                      background=[('selected', '#333333')],
                      foreground=[('selected', '#FFFFFF')])
        self.style.configure('TEntry', 
                            fieldbackground='#222222', 
                            foreground='#CCCCCC',
                            insertcolor='#CCCCCC')
        self.style.configure('TCombobox', 
                            fieldbackground='#222222', 
                            foreground='#CCCCCC')
        self.style.configure('TButton', 
                            background='#333333', 
                            foreground='#CCCCCC',
                            borderwidth=1,
                            relief="flat")
        self.style.configure('Accent.TButton', 
                            background='#03DAC6', 
                            foreground='#000000')
        self.style.configure('Delete.TButton', 
                            background='#CF6679', 
                            foreground='#000000')
        self.style.configure('Treeview', 
                            background='#222222', 
                            foreground='#CCCCCC',
                            fieldbackground='#222222',
                            rowheight=20)
        self.style.configure('Treeview.Heading', 
                            background='#333333', 
                            foreground='#CCCCCC')
        self.style.map('Treeview', 
                      background=[('selected', '#03DAC6')],
                      foreground=[('selected', '#000000')])
        
        # Init data
        self.venvs = {}
        self.current_dir = str(Path.home())
        
        # Create notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_tab()
        self.manage_tab()
        
        # Load venvs and start system scan
        self.load_venvs()
        threading.Thread(target=self.scan_system_for_venvs, daemon=True).start()
    
    def create_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Create")
        
        # Directory
        ttk.Label(tab, text="Directory:").pack(anchor="w", pady=(5,0))
        self.dir_entry = ttk.Entry(tab)
        self.dir_entry.pack(fill="x", pady=5)
        self.dir_entry.insert(0, self.current_dir)
        
        ttk.Button(tab, text="Browse", command=self.browse_dir, width=10).pack(pady=5)
        
        # Venv name
        ttk.Label(tab, text="Venv Name:").pack(anchor="w", pady=(5,0))
        self.venv_name = ttk.Entry(tab)
        self.venv_name.pack(fill="x", pady=5)
        self.venv_name.insert(0, "venv")
        
        ttk.Button(tab, text="Create Venv", command=self.create_venv, 
                  style="Accent.TButton", width=15).pack(pady=10)
    
    def manage_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Manage")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Top frame for venv selection and buttons
        top_frame = ttk.Frame(tab)
        top_frame.grid(row=0, column=0, sticky="ew", pady=5)
        top_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(top_frame, text="Select Venv:").grid(row=0, column=0, sticky="w", padx=(0,5))
        
        # Venv selection combo
        self.venv_combo = ttk.Combobox(top_frame, state="readonly")
        self.venv_combo.grid(row=0, column=1, sticky="ew", padx=5)
        self.venv_combo.bind("<<ComboboxSelected>>", self.on_venv_selected)
        
        # Action buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.grid(row=0, column=2, sticky="e")
        
        ttk.Button(btn_frame, text="🗑️", command=self.delete_venv, 
                  style="Delete.TButton", width=2).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="📂", command=self.open_in_filesystem, 
                  width=2).pack(side="left", padx=2)
        
        # Command frame
        cmd_frame = ttk.Frame(tab)
        cmd_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        ttk.Label(cmd_frame, text="Pip Command:").pack(side="left", padx=(0,5))
        self.cmd_entry = ttk.Entry(cmd_frame)
        self.cmd_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.cmd_entry.bind("<Return>", lambda e: self.run_pip())
        self.cmd_entry.insert(0, "install")
        
        ttk.Button(cmd_frame, text="▶", command=self.run_pip, width=2).pack(side="left")
        
        # Packages frame
        packages_frame = ttk.LabelFrame(tab, text="Installed Packages")
        packages_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        packages_frame.grid_columnconfigure(0, weight=1)
        packages_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview for packages
        self.package_tree = ttk.Treeview(packages_frame, columns=("version",), show="headings", height=6)
        self.package_tree.heading("#0", text="Package", anchor="w")
        self.package_tree.heading("version", text="Version", anchor="w")
        self.package_tree.column("#0", width=150, stretch=tk.YES)
        self.package_tree.column("version", width=80, stretch=tk.NO)
        
        vsb = ttk.Scrollbar(packages_frame, orient="vertical", command=self.package_tree.yview)
        self.package_tree.configure(yscrollcommand=vsb.set)
        
        self.package_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(tab, textvariable=self.status_var, 
                             anchor="w", style='TLabel')
        status_bar.grid(row=3, column=0, sticky="ew", pady=(5,0))
    
    def browse_dir(self):
        dir = filedialog.askdirectory(initialdir=self.current_dir)
        if dir:
            self.current_dir = dir
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, dir)
    
    def create_venv(self):
        venv_name = self.venv_name.get().strip()
        if not venv_name:
            self.status_var.set("Error: Enter venv name")
            return
            
        venv_path = os.path.join(self.current_dir, venv_name)
        
        if os.path.exists(venv_path):
            self.status_var.set("Error: Path already exists")
            return
            
        threading.Thread(target=self._create_venv, args=(venv_path, venv_name), daemon=True).start()
    
    def _create_venv(self, path, name):
        self.status_var.set(f"Creating {name}...")
        
        try:
            # Create venv
            subprocess.run([sys.executable, "-m", "venv", path], check=True)
            self.venvs[name] = path
            self.save_venvs()
            self.update_combo()
            self.status_var.set(f"Created venv: {name}")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
    
    def on_venv_selected(self, event=None):
        venv = self.venv_combo.get()
        if not venv:
            return
            
        path = self.venvs.get(venv)
        if not path:
            self.status_var.set("Error: Venv not found")
            return
            
        # Clear previous packages
        for item in self.package_tree.get_children():
            self.package_tree.delete(item)
            
        # Load installed packages
        pip = os.path.join(path, "bin", "pip")
        threading.Thread(target=self._load_packages, args=(pip,), daemon=True).start()
    
    def _load_packages(self, pip):
        try:
            result = subprocess.run(f"{pip} list --format=json", shell=True, capture_output=True, text=True)
            if result.stderr:
                self.status_var.set(f"Error: {result.stderr[:60]}...")
                return
                
            packages = json.loads(result.stdout)
            
            # Update package tree in main thread
            self.root.after(0, self._update_package_tree, packages)
        except Exception as e:
            self.status_var.set(f"Error: {str(e)[:60]}...")
    
    def _update_package_tree(self, packages):
        # Sort packages alphabetically
        packages.sort(key=lambda p: p['name'].lower())
        
        for pkg in packages:
            self.package_tree.insert("", "end", 
                                   text=pkg['name'], 
                                   values=(pkg['version'],))
        
        self.status_var.set(f"Loaded {len(packages)} packages")
    
    def run_pip(self):
        venv = self.venv_combo.get()
        cmd = self.cmd_entry.get().strip()
        
        if not venv:
            self.status_var.set("Error: Select a venv first")
            return
            
        if not cmd:
            self.status_var.set("Error: Enter pip command")
            return
            
        path = self.venvs.get(venv)
        if not path:
            self.status_var.set("Error: Venv not found")
            return
            
        pip = os.path.join(path, "bin", "pip")
        threading.Thread(target=self._run_pip, args=(pip, cmd), daemon=True).start()
    
    def _run_pip(self, pip, cmd):
        self.status_var.set(f"Running: pip {cmd}...")
        
        try:
            result = subprocess.run(f"{pip} {cmd}", shell=True, capture_output=True, text=True)
            if result.stderr: 
                self.status_var.set(f"Error: {result.stderr[:60]}...")
            
            # Refresh package list if install/uninstall command
            if "install" in cmd or "uninstall" in cmd:
                self.root.after(1000, self.on_venv_selected)
            else:
                self.status_var.set("Command completed")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)[:60]}...")
    
    def delete_venv(self):
        venv = self.venv_combo.get()
        if not venv:
            self.status_var.set("Error: Select a venv to delete")
            return
            
        path = self.venvs.get(venv)
        if not path:
            self.status_var.set("Error: Venv not found")
            return
            
        if not messagebox.askyesno("Confirm Delete", f"Delete venv '{venv}' at {path}?"):
            return
            
        try:
            # Recursive deletion
            import shutil
            shutil.rmtree(path)
            
            # Remove from venvs
            if venv in self.venvs:
                del self.venvs[venv]
                self.save_venvs()
                self.update_combo()
                
                # Clear package list
                for item in self.package_tree.get_children():
                    self.package_tree.delete(item)
                
                self.status_var.set(f"Deleted venv: {venv}")
            else:
                self.status_var.set("Error: Venv not in list")
        except Exception as e:
            self.status_var.set(f"Error deleting venv: {str(e)[:60]}...")
    
    def open_in_filesystem(self):
        venv = self.venv_combo.get()
        if not venv:
            self.status_var.set("Error: Select a venv to open")
            return
            
        path = self.venvs.get(venv)
        if not path:
            self.status_var.set("Error: Venv not found")
            return
            
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            self.status_var.set(f"Opened: {venv}")
        except Exception as e:
            self.status_var.set(f"Error opening: {str(e)[:60]}...")
    
    def scan_system_for_venvs(self):
        """Fast system scan for venv directories"""
        self.status_var.set("Scanning for venvs...")
        
        # Common venv names
        venv_names = ['venv', '.venv', 'env', '.env']
        
        # Search in common locations
        search_paths = [
            str(Path.home()),
            str(Path.home() / "Projects"),
            str(Path.home() / "Desktop"),
            "/opt",
            "/usr/local"
        ]
        
        # Walk through directories
        for path in search_paths:
            if not os.path.isdir(path): continue
                
            for root, dirs, _ in os.walk(path, followlinks=False):
                for name in venv_names:
                    if name in dirs:
                        venv_path = os.path.join(root, name)
                        key = f"{os.path.basename(root)}/{name}"
                        
                        # Add only if not already in list
                        if key not in self.venvs:
                            self.venvs[key] = venv_path
        
        self.save_venvs()
        self.update_combo()
        self.status_var.set(f"Found {len(self.venvs)} venvs")
    
    def load_venvs(self):
        if os.path.exists("venvs.json"):
            try:
                with open("venvs.json") as f:
                    self.venvs = json.load(f)
                self.update_combo()
            except Exception as e:
                self.status_var.set(f"Error loading venvs: {str(e)}")
    
    def save_venvs(self):
        with open("venvs.json", "w") as f:
            json.dump(self.venvs, f, indent=2)
    
    def update_combo(self):
        venv_list = list(self.venvs.keys())
        self.venv_combo["values"] = venv_list
        if venv_list:
            self.venv_combo.current(0)
            self.on_venv_selected()
        else:
            self.status_var.set("No venvs found. Create one!")

if __name__ == "__main__":
    root = tk.Tk()
    FastVenvManager(root)
    root.mainloop()
