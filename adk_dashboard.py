import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import subprocess
import threading
import time

# Configuration Paths
CONFIG_PATH = os.path.join("code", "config", "config.json")
AGENTS_DIR = os.path.join("code", "agents")
CLASSPATH = os.path.join("code")

class ADKDashboard(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ADK Dashboard")
        self.geometry("1000x700")
        self.configure(bg="#2b2b2b")

        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#2b2b2b")
        self.style.configure("TLabel", background="#2b2b2b", foreground="white", font=("Segoe UI", 10))
        self.style.configure("TButton", background="#3c3f41", foreground="white", borderwidth=1)
        self.style.map("TButton", background=[("active", "#4c5052")])
        
        self.style.configure("Accent.TButton", background="#4CAF50", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.map("Accent.TButton", background=[("active", "#45a049")])
        self.style.configure("TNotebook", background="#2b2b2b", borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#3c3f41", foreground="white", padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", "#4c5052")])

        # Data
        self.agent_processes = {}
        self.config_data = {}

        # UI Layout
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        # Main Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabs
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_config = ttk.Frame(self.notebook)
        self.tab_agents = ttk.Frame(self.notebook)
        self.tab_logs = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.notebook.add(self.tab_config, text="Configuration")
        self.notebook.add(self.tab_agents, text="Agents")
        self.notebook.add(self.tab_logs, text="Logs")

        self.setup_dashboard_tab()
        self.setup_config_tab()
        self.setup_agents_tab()
        self.setup_logs_tab()

    def setup_dashboard_tab(self):
        frame = ttk.Frame(self.tab_dashboard)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Welcome to ADK Dashboard", font=("Segoe UI", 24, "bold")).pack(pady=20)
        
        self.lbl_status = ttk.Label(frame, text="Status: Ready", font=("Segoe UI", 12))
        self.lbl_status.pack(pady=5)
        
        btn_refresh = ttk.Button(frame, text="Refresh Status", command=self.load_config)
        btn_refresh.pack(pady=10)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=20)

        ttk.Label(frame, text="Tools", font=("Segoe UI", 14, "bold")).pack(pady=10)
        btn_evaluator = ttk.Button(frame, text="Launch Agent Evaluator", command=self.launch_evaluator, style="Accent.TButton")
        btn_evaluator.pack(pady=10)

    def launch_evaluator(self):
        try:
            subprocess.Popen(["python", "adk_evaluator_gui.py"])
            self.log("Launched ADK Evaluator", "SYSTEM")
        except Exception as e:
            self.log(f"Failed to launch evaluator: {e}", "ERROR")

    def setup_config_tab(self):
        frame = ttk.Frame(self.tab_config)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.txt_config = scrolledtext.ScrolledText(frame, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", font=("Consolas", 10))
        self.txt_config.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Save Configuration", command=self.save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Reload", command=self.load_config).pack(side=tk.RIGHT, padx=5)

    def setup_agents_tab(self):
        frame = ttk.Frame(self.tab_agents)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        columns = ("Agent Name", "Status", "Action")
        self.tree_agents = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        self.tree_agents.heading("Agent Name", text="Agent Name")
        self.tree_agents.heading("Status", text="Status")
        self.tree_agents.heading("Action", text="Action")
        
        self.tree_agents.column("Agent Name", width=200)
        self.tree_agents.column("Status", width=100)
        self.tree_agents.column("Action", width=100)
        
        self.tree_agents.pack(fill=tk.BOTH, expand=True, pady=10)

        # Define Agents
        self.agents = ["IngestionAgent", "QueryAgent", "InsightAgent", "PresentationAgent"]
        
        # Controls
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="Start Selected", command=self.start_selected_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop Selected", command=self.stop_selected_agent).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Build All Agents", command=self.build_agents).pack(side=tk.RIGHT, padx=5)

        self.refresh_agent_list()

    def setup_logs_tab(self):
        frame = ttk.Frame(self.tab_logs)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.txt_logs = scrolledtext.ScrolledText(frame, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", font=("Consolas", 9))
        self.txt_logs.pack(fill=tk.BOTH, expand=True)
        self.txt_logs.tag_config("INFO", foreground="#6a9955")
        self.txt_logs.tag_config("ERROR", foreground="#f44747")
        self.txt_logs.tag_config("SYSTEM", foreground="#569cd6")

    def log(self, message, level="INFO"):
        self.txt_logs.insert(tk.END, f"[{level}] {message}\n", level)
        self.txt_logs.see(tk.END)

    def load_config(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    self.config_data = json.load(f)
                    content = json.dumps(self.config_data, indent=2)
                    self.txt_config.delete("1.0", tk.END)
                    self.txt_config.insert(tk.END, content)
                    
                    self.log("Configuration loaded successfully.", "SYSTEM")
            else:
                self.log(f"Config file not found at {CONFIG_PATH}", "ERROR")
        except Exception as e:
            self.log(f"Error loading config: {e}", "ERROR")

    def save_config(self):
        try:
            content = self.txt_config.get("1.0", tk.END)
            json_content = json.loads(content)
            with open(CONFIG_PATH, 'w') as f:
                json.dump(json_content, f, indent=2)
            self.config_data = json_content
            self.log("Configuration saved.", "SYSTEM")
            messagebox.showinfo("Success", "Configuration saved successfully.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def refresh_agent_list(self):
        for item in self.tree_agents.get_children():
            self.tree_agents.delete(item)
            
        for agent in self.agents:
            status = "Running" if agent in self.agent_processes and self.agent_processes[agent].poll() is None else "Stopped"
            self.tree_agents.insert("", tk.END, values=(agent, status, "Select to Control"))

    def build_agents(self):
        # Python doesn't need compilation, but we can check syntax
        def run_build():
            self.log("Checking Python syntax...", "SYSTEM")
            try:
                py_files = []
                for root, dirs, files in os.walk(os.path.join("code")):
                    for file in files:
                        if file.endswith(".py"):
                            py_files.append(os.path.join(root, file))
                
                if not py_files:
                    self.log("No Python files found.", "ERROR")
                    return

                errors = False
                for py_file in py_files:
                    cmd = ["python", "-m", "py_compile", py_file]
                    process = subprocess.run(cmd, capture_output=True, text=True)
                    if process.returncode != 0:
                        self.log(f"Syntax error in {py_file}:\n{process.stderr}", "ERROR")
                        errors = True
                
                if not errors:
                    self.log("Syntax check successful.", "SYSTEM")
                    messagebox.showinfo("Build", "Agents syntax check passed.")
                else:
                    messagebox.showerror("Build Failed", "Syntax errors found. Check logs.")
            except Exception as e:
                self.log(f"Build error: {e}", "ERROR")

        threading.Thread(target=run_build, daemon=True).start()

    def start_selected_agent(self):
        selected = self.tree_agents.selection()
        if not selected:
            return
        
        item = self.tree_agents.item(selected[0])
        agent_name = item['values'][0]
        
        if agent_name in self.agent_processes and self.agent_processes[agent_name].poll() is None:
            self.log(f"{agent_name} is already running.", "INFO")
            return

        def run_agent():
            self.log(f"Starting {agent_name}...", "SYSTEM")
            try:
                # Map agent name to python file
                # IngestionAgent -> ingestion_agent.py
                script_name = f"{agent_name.replace('Agent', '_agent').lower()}.py"
                script_path = os.path.join("code", "agents", script_name)
                
                if not os.path.exists(script_path):
                     self.log(f"Script not found: {script_path}", "ERROR")
                     return

                cmd = ["python", script_path]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
                self.agent_processes[agent_name] = process
                
                # Update UI
                self.after(0, self.refresh_agent_list)
                
                # Read logs
                for line in iter(process.stdout.readline, ''):
                    self.after(0, lambda l=line: self.log(f"[{agent_name}] {l.strip()}"))
                
                process.stdout.close()
                process.wait()
                self.after(0, lambda: self.log(f"{agent_name} stopped.", "SYSTEM"))
                self.after(0, self.refresh_agent_list)
                
            except Exception as e:
                self.after(0, lambda: self.log(f"Failed to start {agent_name}: {e}", "ERROR"))

        threading.Thread(target=run_agent, daemon=True).start()

    def stop_selected_agent(self):
        selected = self.tree_agents.selection()
        if not selected:
            return
        
        item = self.tree_agents.item(selected[0])
        agent_name = item['values'][0]
        
        if agent_name in self.agent_processes:
            process = self.agent_processes[agent_name]
            if process.poll() is None:
                process.terminate()
                self.log(f"Stopping {agent_name}...", "SYSTEM")
            else:
                self.log(f"{agent_name} is not running.", "INFO")
        else:
            self.log(f"{agent_name} is not running.", "INFO")

if __name__ == "__main__":
    app = ADKDashboard()
    app.mainloop()
