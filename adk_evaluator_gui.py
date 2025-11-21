import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from datetime import datetime

# --- Configuration & Theme ---
THEME_COLOR = "#2b2b2b"  # Neutral Grey Background
ACCENT_COLOR = "#4CAF50" # Vibrant Green for success/active
TEXT_COLOR = "#ffffff"
SECONDARY_COLOR = "#3c3f41" # Slightly lighter grey for panels
HIGHLIGHT_COLOR = "#2196F3" # Blue for active elements
FONT_MAIN = ("Segoe UI", 10)
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_TITLE = ("Segoe UI", 18, "bold")

class ADKEvaluatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google ADK Agent Evaluator")
        self.root.geometry("1200x800")
        self.root.configure(bg=THEME_COLOR)

        self.is_monitoring = False
        self.metrics_history = {"latency": [], "accuracy": []}
        
        self._setup_styles()
        self._build_layout()
        
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=THEME_COLOR)
        style.configure("TLabel", background=THEME_COLOR, foreground=TEXT_COLOR, font=FONT_MAIN)
        style.configure("Header.TLabel", font=FONT_HEADER, foreground=ACCENT_COLOR)
        style.configure("Title.TLabel", font=FONT_TITLE, foreground=TEXT_COLOR)
        
        style.configure("Card.TFrame", background=SECONDARY_COLOR, relief="flat")
        style.configure("Card.TLabel", background=SECONDARY_COLOR, foreground=TEXT_COLOR)
        
        style.configure("TButton", font=FONT_MAIN, background=SECONDARY_COLOR, foreground=TEXT_COLOR, borderwidth=0)
        style.map("TButton", background=[('active', HIGHLIGHT_COLOR)])
        
        style.configure("Accent.TButton", background=ACCENT_COLOR, foreground="white")
        style.map("Accent.TButton", background=[('active', "#45a049")])

    def _build_layout(self):
        # Main Container
        main_container = ttk.Frame(self.root, padding=20)
        main_container.pack(fill="both", expand=True)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="ADK Agent Evaluation Dashboard", style="Title.TLabel")
        title_label.pack(side="left")
        
        self.status_indicator = ttk.Label(header_frame, text="● Offline", foreground="red", font=("Segoe UI", 10, "bold"))
        self.status_indicator.pack(side="right", padx=10)
        
        self.monitor_btn = ttk.Button(header_frame, text="Start Live Monitoring", style="Accent.TButton", command=self.toggle_monitoring)
        self.monitor_btn.pack(side="right")

        # Content Grid
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill="both", expand=True)
        
        # Left Column: Hard Metrics
        left_col = ttk.Frame(content_frame, width=400)
        left_col.pack(side="left", fill="y", padx=(0, 10))
        
        self._build_hard_metrics_panel(left_col)
        
        # Middle Column: Soft Metrics & Trajectory
        mid_col = ttk.Frame(content_frame)
        mid_col.pack(side="left", fill="both", expand=True, padx=10)
        
        self._build_soft_metrics_panel(mid_col)
        self._build_trajectory_panel(mid_col)
        
        # Right Column: Visualizations (Graphs)
        right_col = ttk.Frame(content_frame, width=350)
        right_col.pack(side="right", fill="y", padx=(10, 0))
        
        self._build_visualization_panel(right_col)

    def _build_card(self, parent, title):
        card = ttk.Frame(parent, style="Card.TFrame", padding=15)
        card.pack(fill="x", pady=5)
        
        lbl = ttk.Label(card, text=title, style="Header.TLabel", background=SECONDARY_COLOR)
        lbl.pack(anchor="w", pady=(0, 10))
        return card

    def _build_hard_metrics_panel(self, parent):
        # Accuracy
        acc_card = self._build_card(parent, "Final Output Quality (Accuracy)")
        self.accuracy_bar = ttk.Progressbar(acc_card, orient="horizontal", length=300, mode="determinate")
        self.accuracy_bar.pack(fill="x", pady=5)
        self.accuracy_label = ttk.Label(acc_card, text="0%", style="Card.TLabel", font=("Segoe UI", 24, "bold"))
        self.accuracy_label.pack(anchor="e")
        
        # Latency
        lat_card = self._build_card(parent, "Latency (Response Time)")
        self.latency_val = ttk.Label(lat_card, text="0.00s", style="Card.TLabel", font=("Segoe UI", 24, "bold"), foreground="#FFC107")
        self.latency_val.pack(anchor="center")
        
        # Cost
        cost_card = self._build_card(parent, "Resource Efficiency (Cost)")
        self.cost_val = ttk.Label(cost_card, text="$0.0000", style="Card.TLabel", font=("Segoe UI", 20), foreground="#03A9F4")
        self.cost_val.pack(anchor="center")
        
        # Robustness
        rob_card = self._build_card(parent, "Robustness Score")
        self.robustness_bar = ttk.Progressbar(rob_card, orient="horizontal", length=300, mode="determinate")
        self.robustness_bar.pack(fill="x", pady=5)
        self.robustness_label = ttk.Label(rob_card, text="N/A", style="Card.TLabel")
        self.robustness_label.pack(anchor="e")

    def _build_soft_metrics_panel(self, parent):
        soft_card = self._build_card(parent, "Qualitative Metrics (Soft)")
        
        # Reasoning Clarity
        r_frame = ttk.Frame(soft_card, style="Card.TFrame")
        r_frame.pack(fill="x", pady=2)
        ttk.Label(r_frame, text="Reasoning Clarity", style="Card.TLabel").pack(side="left")
        self.reasoning_score = ttk.Label(r_frame, text="★★☆☆☆", style="Card.TLabel", foreground="#FFD700")
        self.reasoning_score.pack(side="right")
        
        # Collaboration
        c_frame = ttk.Frame(soft_card, style="Card.TFrame")
        c_frame.pack(fill="x", pady=2)
        ttk.Label(c_frame, text="Collaboration Quality", style="Card.TLabel").pack(side="left")
        self.collab_score = ttk.Label(c_frame, text="Pending", style="Card.TLabel")
        self.collab_score.pack(side="right")
        
        # User Satisfaction (NPS)
        n_frame = ttk.Frame(soft_card, style="Card.TFrame")
        n_frame.pack(fill="x", pady=2)
        ttk.Label(n_frame, text="User Satisfaction (NPS)", style="Card.TLabel").pack(side="left")
        self.nps_score = ttk.Label(n_frame, text="--", style="Card.TLabel")
        self.nps_score.pack(side="right")

    def _build_trajectory_panel(self, parent):
        traj_card = self._build_card(parent, "Agent Trajectory & Decisions")
        
        # Text area for logs
        self.log_text = tk.Text(traj_card, height=15, bg="#1e1e1e", fg="#dcdcdc", 
                                font=("Consolas", 9), borderwidth=0, highlightthickness=0)
        self.log_text.pack(fill="both", expand=True)
        
        # Scrollbar
        # (Optional: Add scrollbar if needed, but keeping it clean for now)

    def _build_visualization_panel(self, parent):
        viz_card = self._build_card(parent, "Live Performance")
        
        self.canvas = tk.Canvas(viz_card, bg="#1e1e1e", height=200, highlightthickness=0)
        self.canvas.pack(fill="x", pady=5)
        
        ttk.Label(viz_card, text="Latency Trend (Last 20 req)", style="Card.TLabel", font=("Segoe UI", 8)).pack()

    def toggle_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_btn.configure(text="Stop Monitoring", style="TButton")
            self.status_indicator.configure(text="● Live", foreground=ACCENT_COLOR)
            # Start simulation thread
            self.thread = threading.Thread(target=self.simulate_data_stream, daemon=True)
            self.thread.start()
        else:
            self.is_monitoring = False
            self.monitor_btn.configure(text="Start Live Monitoring", style="Accent.TButton")
            self.status_indicator.configure(text="● Offline", foreground="red")

    def simulate_data_stream(self):
        """Simulates incoming agent data for demonstration."""
        steps = [
            "Analyzing user request...",
            "Retrieving context from vector DB...",
            "Formulating plan...",
            "Executing tool: SearchWeb...",
            "Processing search results...",
            "Generating final response...",
            "Validating output..."
        ]
        
        while self.is_monitoring:
            # Simulate Hard Metrics
            accuracy = random.randint(70, 99)
            latency = random.uniform(0.5, 3.5)
            cost = random.uniform(0.001, 0.05)
            robustness = random.randint(80, 100)
            
            # Simulate Soft Metrics
            reasoning_stars = "★" * random.randint(3, 5) + "☆" * (5 - random.randint(3, 5)) # Simplified
            reasoning_stars = "★" * int(accuracy / 20) + "☆" * (5 - int(accuracy / 20))
            
            # Update GUI safely
            self.root.after(0, self.update_metrics, accuracy, latency, cost, robustness, reasoning_stars)
            
            # Log update
            step_msg = f"[{datetime.now().strftime('%H:%M:%S')}] {random.choice(steps)}"
            self.root.after(0, self.log_message, step_msg)
            
            # Update Graph Data
            self.metrics_history["latency"].append(latency)
            if len(self.metrics_history["latency"]) > 20:
                self.metrics_history["latency"].pop(0)
            self.root.after(0, self.draw_graph)
            
            time.sleep(1.5)

    def update_metrics(self, acc, lat, cost, rob, reasoning):
        self.accuracy_bar['value'] = acc
        self.accuracy_label.configure(text=f"{acc}%")
        
        self.latency_val.configure(text=f"{lat:.2f}s")
        self.cost_val.configure(text=f"${cost:.4f}")
        
        self.robustness_bar['value'] = rob
        self.robustness_label.configure(text=f"{rob}/100")
        
        self.reasoning_score.configure(text=reasoning)
        self.collab_score.configure(text=f"{random.randint(85, 100)}%")
        self.nps_score.configure(text=f"{random.randint(1, 10)}")

    def log_message(self, msg):
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    def draw_graph(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        data = self.metrics_history["latency"]
        
        if not data: return
        
        max_val = max(data) if max(data) > 0 else 1
        points = []
        dx = w / (len(data) - 1) if len(data) > 1 else w
        
        for i, val in enumerate(data):
            x = i * dx
            y = h - (val / max_val * h * 0.8) # Scale to 80% height
            points.extend([x, y])
            
        if len(points) >= 4:
            self.canvas.create_line(points, fill=ACCENT_COLOR, width=2, smooth=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = ADKEvaluatorGUI(root)
    root.mainloop()
