"""
Long-Term Memory GUI - Comprehensive Tkinter Interface
Displays and manages all memory types with full parameter visibility
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading

try:
    from long_term_memory import LongTermMemory
    from memory_utils import MemoryUtils
except ImportError:
    print("Warning: Memory modules not found. GUI will run in demo mode.")
    LongTermMemory = None
    MemoryUtils = None


class LongTermMemoryGUI:
    """Main GUI for Long-Term Memory System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AI Agent Long-Term Memory System")
        self.root.geometry("1400x900")
        
        # Colors - Dark theme
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#e0e0e0',
            'accent': '#0e639c',
            'accent_hover': '#1177bb',
            'panel': '#2d2d2d',
            'border': '#3e3e3e',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'episodic': '#2196f3',
            'semantic': '#9c27b0',
            'procedural': '#ff5722'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize variables
        self.memory_system = None
        self.utils = None
        self.current_view = 'episodic'  # episodic, semantic, procedural
        self.selected_memory = None
        
        # Create GUI first (needed for logging)
        self.create_gui()
        
        # Then initialize memory system
        self.initialize_memory_system()
        self.refresh_all()
    
    def initialize_memory_system(self):
        """Initialize the long-term memory system"""
        try:
            if LongTermMemory:
                self.memory_system = LongTermMemory()
                self.utils = MemoryUtils()
                self.log("✓ Memory system initialized successfully")
            else:
                self.log("⚠ Running in demo mode - memory  modules not available")
        except Exception as e:
            self.log(f"✗ Error initializing memory system: {e}")
    
    def create_gui(self):
        """Create the main GUI layout"""
        # Top toolbar
        self.create_toolbar()
        
        # Main content area (split)
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, 
                                    bg=self.colors['bg'], sashwidth=3)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Memory browser and stats
        left_panel = tk.Frame(main_paned, bg=self.colors['bg'])
        main_paned.add(left_panel, width=900)
        
        # Right panel: Details and controls
        right_panel = tk.Frame(main_paned, bg=self.colors['bg'])
        main_paned.add(right_panel, width=480)
        
        # Build left panel
        self.create_stats_panel(left_panel)
        self.create_memory_browser(left_panel)
        
        # Build right panel
        self.create_details_panel(right_panel)
        self.create_controls_panel(right_panel)
        
        # Bottom status bar
        self.create_status_bar()
    
    def create_toolbar(self):
        """Create top toolbar with actions"""
        toolbar = tk.Frame(self.root, bg=self.colors['panel'], height=50)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Title
        title = tk.Label(toolbar, text="🧠 Long-Term Memory System", 
                        bg=self.colors['panel'], fg=self.colors['fg'],
                        font=('Arial', 14, 'bold'))
        title.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(toolbar, bg=self.colors['panel'])
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        buttons = [
            ("➕ Add Memory", self.show_add_memory_dialog),
            ("🔄 Refresh", self.refresh_all),
            ("🔍 Search", self.show_search_dialog),
            ("💾 Export", self.export_memories),
            ("📥 Import", self.import_memories),
            ("⚙️ Settings", self.show_settings),
        ]
        
        for text, command in buttons:
            btn = tk.Button(btn_frame, text=text, command=command,
                          bg=self.colors['accent'], fg='white',
                          font=('Arial', 9), relief=tk.FLAT,
                          cursor='hand2', padx=10, pady=5)
            btn.pack(side=tk.LEFT, padx=2)
            
            # Hover effects
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=self.colors['accent_hover']))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg=self.colors['accent']))
    
    def create_stats_panel(self, parent):
        """Create statistics overview panel"""
        stats_frame = tk.LabelFrame(parent, text="📊 Statistics", 
                                   bg=self.colors['panel'], fg=self.colors['fg'],
                                   font=('Arial', 10, 'bold'), relief=tk.FLAT,
                                   borderwidth=1)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Stats display
        self.stats_labels = {}
        stats_container = tk.Frame(stats_frame, bg=self.colors['panel'])
        stats_container.pack(fill=tk.X, padx=10, pady=10)
        
        stats = [
            ("Total Memories", "total", self.colors['fg']),
            ("Episodic", "episodic", self.colors['episodic']),
            ("Semantic", "semantic", self.colors['semantic']),
            ("Procedural", "procedural", self.colors['procedural']),
            ("DB Size", "db_size", self.colors['warning']),
        ]
        
        for i, (label, key, color) in enumerate(stats):
            frame = tk.Frame(stats_container, bg=self.colors['panel'])
            frame.grid(row=0, column=i, padx=15, pady=5)
            
            lbl = tk.Label(frame, text=label, bg=self.colors['panel'],
                          fg=self.colors['fg'], font=('Arial', 8))
            lbl.pack()
            
            value_lbl = tk.Label(frame, text="0", bg=self.colors['panel'],
                               fg=color, font=('Arial', 16, 'bold'))
            value_lbl.pack()
            self.stats_labels[key] = value_lbl
    
    def create_memory_browser(self, parent):
        """Create memory browser with tabs for each type"""
        browser_frame = tk.LabelFrame(parent, text="📚 Memory Browser",
                                     bg=self.colors['panel'], fg=self.colors['fg'],
                                     font=('Arial', 10, 'bold'), relief=tk.FLAT)
        browser_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab control
        self.notebook = ttk.Notebook(browser_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Style the notebook
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.colors['panel'], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors['bg'], 
                       foreground=self.colors['fg'], padding=[20, 10])
        style.map('TNotebook.Tab', background=[('selected', self.colors['accent'])])
        
        # Create tabs for each memory type
        self.episodic_tab = self.create_episodic_tab()
        self.semantic_tab = self.create_semantic_tab()
        self.procedural_tab = self.create_procedural_tab()
        
        self.notebook.add(self.episodic_tab, text="🎬 Episodic")
        self.notebook.add(self.semantic_tab, text="📖 Semantic")
        self.notebook.add(self.procedural_tab, text="⚙️ Procedural")
        
        # Track tab changes
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def create_episodic_tab(self):
        """Create episodic memory browser tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        # Treeview for episodic memories
        columns = ('ID', 'Timestamp', 'Description', 'Importance', 'Retrieval Count')
        self.episodic_tree = ttk.Treeview(tab, columns=columns, show='headings',
                                         selectmode='browse', height=15)
        
        # Configure columns
        self.episodic_tree.heading('ID', text='ID')
        self.episodic_tree.heading('Timestamp', text='Timestamp')
        self.episodic_tree.heading('Description', text='Event Description')
        self.episodic_tree.heading('Importance', text='Importance')
        self.episodic_tree.heading('Retrieval Count', text='Retrieved')
        
        self.episodic_tree.column('ID', width=50, anchor='center')
        self.episodic_tree.column('Timestamp', width=150, anchor='w')
        self.episodic_tree.column('Description', width=400, anchor='w')
        self.episodic_tree.column('Importance', width=80, anchor='center')
        self.episodic_tree.column('Retrieval Count', width=80, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.episodic_tree.yview)
        self.episodic_tree.configure(yscrollcommand=scrollbar.set)
        
        self.episodic_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind selection event
        self.episodic_tree.bind('<<TreeviewSelect>>', self.on_memory_selected)
        
        # Style treeview
        style = ttk.Style()
        style.configure("Treeview", background=self.colors['bg'],
                       foreground=self.colors['fg'], fieldbackground=self.colors['bg'],
                       borderwidth=0)
        style.map('Treeview', background=[('selected', self.colors['accent'])])
        
        return tab
    
    def create_semantic_tab(self):
        """Create semantic memory browser tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        columns = ('ID', 'Concept', 'Definition', 'Confidence', 'Source')
        self.semantic_tree = ttk.Treeview(tab, columns=columns, show='headings',
                                         selectmode='browse', height=15)
        
        self.semantic_tree.heading('ID', text='ID')
        self.semantic_tree.heading('Concept', text='Concept Name')
        self.semantic_tree.heading('Definition', text='Definition')
        self.semantic_tree.heading('Confidence', text='Confidence')
        self.semantic_tree.heading('Source', text='Source')
        
        self.semantic_tree.column('ID', width=50, anchor='center')
        self.semantic_tree.column('Concept', width=150, anchor='w')
        self.semantic_tree.column('Definition', width=400, anchor='w')
        self.semantic_tree.column('Confidence', width=100, anchor='center')
        self.semantic_tree.column('Source', width=150, anchor='w')
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.semantic_tree.yview)
        self.semantic_tree.configure(yscrollcommand=scrollbar.set)
        
        self.semantic_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        self.semantic_tree.bind('<<TreeviewSelect>>', self.on_memory_selected)
        
        return tab
    
    def create_procedural_tab(self):
        """Create procedural memory browser tab"""
        tab = tk.Frame(self.notebook, bg=self.colors['bg'])
        
        columns = ('ID', 'Procedure', 'Description', 'Success Rate', 'Executions')
        self.procedural_tree = ttk.Treeview(tab, columns=columns, show='headings',
                                           selectmode='browse', height=15)
        
        self.procedural_tree.heading('ID', text='ID')
        self.procedural_tree.heading('Procedure', text='Procedure Name')
        self.procedural_tree.heading('Description', text='Description')
        self.procedural_tree.heading('Success Rate', text='Success Rate')
        self.procedural_tree.heading('Executions', text='Executions')
        
        self.procedural_tree.column('ID', width=50, anchor='center')
        self.procedural_tree.column('Procedure', width=150, anchor='w')
        self.procedural_tree.column('Description', width=400, anchor='w')
        self.procedural_tree.column('Success Rate', width=100, anchor='center')
        self.procedural_tree.column('Executions', width=100, anchor='center')
        
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.procedural_tree.yview)
        self.procedural_tree.configure(yscrollcommand=scrollbar.set)
        
        self.procedural_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        self.procedural_tree.bind('<<TreeviewSelect>>', self.on_memory_selected)
        
        return tab
    
    def create_details_panel(self, parent):
        """Create memory details inspection panel"""
        details_frame = tk.LabelFrame(parent, text="🔍 Memory Details",
                                     bg=self.colors['panel'], fg=self.colors['fg'],
                                     font=('Arial', 10, 'bold'), relief=tk.FLAT)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrolled text for displaying all parameters
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD,
                                                      bg=self.colors['bg'],
                                                      fg=self.colors['fg'],
                                                      font=('Consolas', 9),
                                                      height=25, relief=tk.FLAT,
                                                      padx=10, pady=10)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure tags for syntax highlighting
        self.details_text.tag_config('key', foreground=self.colors['accent'], font=('Consolas', 9, 'bold'))
        self.details_text.tag_config('value', foreground=self.colors['fg'])
        self.details_text.tag_config('section', foreground=self.colors['success'], 
                                     font=('Consolas', 10, 'bold'))
    
    def create_controls_panel(self, parent):
        """Create controls panel for memory management"""
        controls_frame = tk.LabelFrame(parent, text="⚙️ Controls",
                                      bg=self.colors['panel'], fg=self.colors['fg'],
                                      font=('Arial', 10, 'bold'), relief=tk.FLAT)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_container = tk.Frame(controls_frame, bg=self.colors['panel'])
        btn_container.pack(fill=tk.X, padx=10, pady=10)
        
        buttons = [
            ("✏️ Edit", self.edit_memory, self.colors['accent']),
            ("🗑️ Delete", self.delete_memory, self.colors['error']),
            ("🔗 Similar", self.find_similar, self.colors['warning']),
            ("💾 Backup", self.backup_database, self.colors['success']),
        ]
        
        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(btn_container, text=text, command=command,
                          bg=color, fg='white', font=('Arial', 9, 'bold'),
                          relief=tk.FLAT, cursor='hand2', width=12, height=2)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
        
        # Configure grid
        btn_container.grid_columnconfigure(0, weight=1)
        btn_container.grid_columnconfigure(1, weight=1)
    
    def create_status_bar(self):
        """Create bottom status bar"""
        self.status_bar = tk.Label(self.root, text="Ready", 
                                  bg=self.colors['panel'], fg=self.colors['fg'],
                                  font=('Arial', 9), anchor='w', padx=10, pady=5)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def refresh_all(self):
        """Refresh all data from memory system"""
        if not self.memory_system:
            return
        
        self.refresh_statistics()
        self.refresh_memory_lists()
        self.log("Refreshed all data")
    
    def refresh_statistics(self):
        """Update statistics display"""
        if not self.memory_system:
            return
        
        try:
            stats = self.memory_system.get_statistics()
            self.stats_labels['total'].config(text=str(stats.get('total_memories', 0)))
            self.stats_labels['episodic'].config(text=str(stats.get('episodic_count', 0)))
            self.stats_labels['semantic'].config(text=str(stats.get('semantic_count', 0)))
            self.stats_labels['procedural'].config(text=str(stats.get('procedural_count', 0)))
            self.stats_labels['db_size'].config(text=f"{stats.get('database_size_mb', 0)} MB")
        except Exception as e:
            self.log(f"Error refreshing statistics: {e}")
    
    def refresh_memory_lists(self):
        """Refresh all memory list views"""
        self.refresh_episodic_list()
        self.refresh_semantic_list()
        self.refresh_procedural_list()
    
    def refresh_episodic_list(self):
        """Refresh episodic memory list"""
        if not self.memory_system:
            return
        
        # Clear existing
        for item in self.episodic_tree.get_children():
            self.episodic_tree.delete(item)
        
        try:
            memories = self.memory_system.db.get_all_episodic_memories(limit=100)
            for memory in memories:
                desc = memory.get('event_description', '')[:60] + '...' if len(memory.get('event_description', '')) > 60 else memory.get('event_description', '')
                timestamp = memory.get('timestamp', '')[:19] if memory.get('timestamp') else ''
                
                self.episodic_tree.insert('', tk.END, values=(
                    memory.get('id', ''),
                    timestamp,
                    desc,
                    f"{memory.get('importance_score', 0):.1f}",
                    memory.get('retrieval_count', 0)
                ))
        except Exception as e:
            self.log(f"Error refreshing episodic list: {e}")
    
    def refresh_semantic_list(self):
        """Refresh semantic memory list"""
        if not self.memory_system:
            return
        
        for item in self.semantic_tree.get_children():
            self.semantic_tree.delete(item)
        
        try:
            memories = self.memory_system.db.get_all_semantic_memories(limit=100)
            for memory in memories:
                definition = memory.get('definition', '')[:50] + '...' if len(memory.get('definition', '')) > 50 else memory.get('definition', '')
                
                self.semantic_tree.insert('', tk.END, values=(
                    memory.get('id', ''),
                    memory.get('concept_name', ''),
                    definition,
                    f"{memory.get('confidence_score', 0):.2f}",
                    memory.get('source', 'N/A')
                ))
        except Exception as e:
            self.log(f"Error refreshing semantic list: {e}")
    
    def refresh_procedural_list(self):
        """Refresh procedural memory list"""
        if not self.memory_system:
            return
        
        for item in self.procedural_tree.get_children():
            self.procedural_tree.delete(item)
        
        try:
            memories = self.memory_system.db.get_all_procedural_memories(limit=100)
            for memory in memories:
                desc = memory.get('description', '')[:50] + '...' if len(memory.get('description', '')) > 50 else memory.get('description', '')
                
                self.procedural_tree.insert('', tk.END, values=(
                    memory.get('id', ''),
                    memory.get('procedure_name', ''),
                    desc,
                    f"{memory.get('success_rate', 0):.1f}%",
                    memory.get('execution_count', 0)
                ))
        except Exception as e:
            self.log(f"Error refreshing procedural list: {e}")
    
    def on_tab_changed(self, event):
        """Handle tab selection change"""
        tab_idx = self.notebook.index(self.notebook.select())
        self.current_view = ['episodic', 'semantic', 'procedural'][tab_idx]
        self.selected_memory = None
        self.details_text.delete(1.0, tk.END)
    
    def on_memory_selected(self, event):
        """Handle memory selection in treeview"""
        tree = event.widget
        selection = tree.selection()
        
        if not selection:
            return
        
        item = tree.item(selection[0])
        memory_id = item['values'][0]
        
        # Fetch full memory details
        self.display_memory_details(memory_id, self.current_view)
    
    def display_memory_details(self, memory_id: int, memory_type: str):
        """Display all parameters of selected memory"""
        if not self.memory_system:
            return
        
        try:
            # Fetch memory based on type
            if memory_type == 'episodic':
                memory = self.memory_system.db.get_episodic_memory(memory_id)
            elif memory_type == 'semantic':
                memory = self.memory_system.db.get_semantic_memory(memory_id)
            else:
                memory = self.memory_system.db.get_procedural_memory(memory_id)
            
            if not memory:
                return
            
            self.selected_memory = memory
            
            # Clear and display
            self.details_text.delete(1.0, tk.END)
            
            # Title
            self.details_text.insert(tk.END, f"═══ {memory_type.upper()} MEMORY #{memory_id} ═══\n\n", 'section')
            
            # Display all fields
            for key, value in memory.items():
                # Format key
                display_key = key.replace('_', ' ').title()
                self.details_text.insert(tk.END, f"{display_key}: ", 'key')
                
                # Format value
                if isinstance(value, list):
                    self.details_text.insert(tk.END, f"{', '.join(map(str, value)) if value else 'None'}\n", 'value')
                elif isinstance(value, dict):
                    self.details_text.insert(tk.END, f"\n{json.dumps(value, indent=2)}\n", 'value')
                else:
                    self.details_text.insert(tk.END, f"{value}\n", 'value')
            
            self.details_text.insert(tk.END, f"\n{'═'*50}\n", 'section')
            
        except Exception as e:
            self.log(f"Error displaying memory details: {e}")
    
    def show_add_memory_dialog(self):
        """Show dialog to add new memory"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Memory")
        dialog.geometry("600x700")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Memory type selection
        tk.Label(dialog, text="Memory Type:", bg=self.colors['bg'], 
                fg=self.colors['fg'], font=('Arial', 10, 'bold')).pack(pady=10)
        
        mem_type_var = tk.StringVar(value='episodic')
        type_frame = tk.Frame(dialog, bg=self.colors['bg'])
        type_frame.pack(pady=5)
        
        for mtype in ['episodic', 'semantic', 'procedural']:
            tk.Radiobutton(type_frame, text=mtype.title(), variable=mem_type_var,
                          value=mtype, bg=self.colors['bg'], fg=self.colors['fg'],
                          selectcolor=self.colors['panel'], font=('Arial', 9)).pack(side=tk.LEFT, padx=10)
        
        # Form fields
        form_frame = tk.Frame(dialog, bg=self.colors['bg'])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Episodic fields
        episodic_frame = tk.Frame(form_frame, bg=self.colors['bg'])
        
        tk.Label(episodic_frame, text="Event Description:", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=0, column=0, sticky='w', pady=5)
        ep_desc = tk.Text(episodic_frame, height=3, width=50, bg=self.colors['panel'],
                         fg=self.colors['fg'])
        ep_desc.grid(row=0, column=1, pady=5)
        
        tk.Label(episodic_frame, text="Context:", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=1, column=0, sticky='w', pady=5)
        ep_context = tk.Entry(episodic_frame, width=50, bg=self.colors['panel'],
                             fg=self.colors['fg'])
        ep_context.grid(row=1, column=1, pady=5)
        
        tk.Label(episodic_frame, text="Importance (0-100):", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=2, column=0, sticky='w', pady=5)
        ep_importance = tk.Scale(episodic_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                bg=self.colors['panel'], fg=self.colors['fg'],
                                length=300)
        ep_importance.set(50)
        ep_importance.grid(row=2, column=1, pady=5)
        
        tk.Label(episodic_frame, text="Tags (comma-separated):", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=3, column=0, sticky='w', pady=5)
        ep_tags = tk.Entry(episodic_frame, width=50, bg=self.colors['panel'],
                          fg=self.colors['fg'])
        ep_tags.grid(row=3, column=1, pady=5)
        
        # Semantic fields
        semantic_frame = tk.Frame(form_frame, bg=self.colors['bg'])
        
        tk.Label(semantic_frame, text="Concept Name:", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=0, column=0, sticky='w', pady=5)
        sem_concept = tk.Entry(semantic_frame, width=50, bg=self.colors['panel'],
                              fg=self.colors['fg'])
        sem_concept.grid(row=0, column=1, pady=5)
        
        tk.Label(semantic_frame, text="Definition:", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=1, column=0, sticky='w', pady=5)
        sem_def = tk.Text(semantic_frame, height=4, width=50, bg=self.colors['panel'],
                         fg=self.colors['fg'])
        sem_def.grid(row=1, column=1, pady=5)
        
        tk.Label(semantic_frame, text="Confidence (0-1):", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=2, column=0, sticky='w', pady=5)
        sem_confidence = tk.Scale(semantic_frame, from_=0, to=1, resolution=0.01,
                                 orient=tk.HORIZONTAL, bg=self.colors['panel'],
                                 fg=self.colors['fg'], length=300)
        sem_confidence.set(0.5)
        sem_confidence.grid(row=2, column=1, pady=5)
        
        # Procedural fields
        procedural_frame = tk.Frame(form_frame, bg=self.colors['bg'])
        
        tk.Label(procedural_frame, text="Procedure Name:", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=0, column=0, sticky='w', pady=5)
        proc_name = tk.Entry(procedural_frame, width=50, bg=self.colors['panel'],
                            fg=self.colors['fg'])
        proc_name.grid(row=0, column=1, pady=5)
        
        tk.Label(procedural_frame, text="Description:", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=1, column=0, sticky='w', pady=5)
        proc_desc = tk.Text(procedural_frame, height=3, width=50, bg=self.colors['panel'],
                           fg=self.colors['fg'])
        proc_desc.grid(row=1, column=1, pady=5)
        
        tk.Label(procedural_frame, text="Steps (one per line):", bg=self.colors['bg'],
                fg=self.colors['fg']).grid(row=2, column=0, sticky='w', pady=5)
        proc_steps = tk.Text(procedural_frame, height=5, width=50, bg=self.colors['panel'],
                            fg=self.colors['fg'])
        proc_steps.grid(row=2, column=1, pady=5)
        
        # Show appropriate form
        def update_form(*args):
            episodic_frame.pack_forget()
            semantic_frame.pack_forget()
            procedural_frame.pack_forget()
            
            if mem_type_var.get() == 'episodic':
                episodic_frame.pack(fill=tk.BOTH, expand=True)
            elif mem_type_var.get() == 'semantic':
                semantic_frame.pack(fill=tk.BOTH, expand=True)
            else:
                procedural_frame.pack(fill=tk.BOTH, expand=True)
        
        mem_type_var.trace('w', update_form)
        update_form()
        
        # Submit button
        def submit():
            try:
                mtype = mem_type_var.get()
                
                if mtype == 'episodic':
                    tags = [t.strip() for t in ep_tags.get().split(',') if t.strip()]
                    self.memory_system.store_episode(
                        ep_desc.get(1.0, tk.END).strip(),
                        context=ep_context.get(),
                        importance_score=float(ep_importance.get()),
                        tags=tags
                    )
                elif mtype == 'semantic':
                    self.memory_system.store_concept(
                        sem_concept.get(),
                        sem_def.get(1.0, tk.END).strip(),
                        confidence_score=float(sem_confidence.get())
                    )
                else:
                    steps = [s.strip() for s in proc_steps.get(1.0, tk.END).split('\n') if s.strip()]
                    self.memory_system.store_procedure(
                        proc_name.get(),
                        proc_desc.get(1.0, tk.END).strip(),
                        steps
                    )
                
                self.refresh_all()
                dialog.destroy()
                self.log(f"✓ Added new {mtype} memory")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add memory: {e}")
        
        tk.Button(dialog, text="Add Memory", command=submit,
                 bg=self.colors['success'], fg='white', font=('Arial', 10, 'bold'),
                 relief=tk.FLAT, cursor='hand2', padx=20, pady=10).pack(pady=20)
    
    def show_search_dialog(self):
        """Show search dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Search Memories")
        dialog.geometry("500x200")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        
        tk.Label(dialog, text="Search Query:", bg=self.colors['bg'],
                fg=self.colors['fg'], font=('Arial', 10)).pack(pady=20)
        
        search_entry = tk.Entry(dialog, width=50, bg=self.colors['panel'],
                               fg=self.colors['fg'], font=('Arial', 10))
        search_entry.pack(pady=10)
        search_entry.focus()
        
        def do_search():
            query = search_entry.get()
            if not query or not self.memory_system:
                return
            
            # Search in current view
            if self.current_view == 'episodic':
                results = self.memory_system.search_episodes(query)
            elif self.current_view == 'semantic':
                results = self.memory_system.search_concepts(query)
            else:
                results = self.memory_system.search_procedures(query)
            
            self.log(f"Found {len(results)} results for '{query}'")
            self.refresh_memory_lists()
            dialog.destroy()
        
        tk.Button(dialog, text="Search", command=do_search,
                 bg=self.colors['accent'], fg='white', font=('Arial', 10),
                 relief=tk.FLAT, cursor='hand2', padx=30, pady=10).pack(pady=20)
    
    def edit_memory(self):
        """Edit selected memory"""
        if not self.selected_memory:
            messagebox.showwarning("No Selection", "Please select a memory to edit")
            return
        
        messagebox.showinfo("Edit", "Edit functionality coming soon!")
    
    def delete_memory(self):
        """Delete selected memory"""
        if not self.selected_memory:
            messagebox.showwarning("No Selection", "Please select a memory to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this memory?"):
            try:
                self.memory_system.delete_memory(
                    self.selected_memory['id'],
                    self.current_view
                )
                self.refresh_all()
                self.selected_memory = None
                self.details_text.delete(1.0, tk.END)
                self.log("✓ Memory deleted")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete memory: {e}")
    
    def find_similar(self):
        """Find similar memories to selected one"""
        if not self.selected_memory:
            messagebox.showwarning("No Selection", "Please select a memory to find similar ones")
            return
        
        try:
            similar = self.memory_system.find_similar_memories(
                self.selected_memory,
                self.current_view,
                limit=5
            )
            self.log(f"Found {len(similar)} similar memories")
            # Could display in a new dialog
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find similar memories: {e}")
    
    def backup_database(self):
        """Create database backup"""
        if not self.memory_system:
            return
        
        try:
            backup_path = self.memory_system.backup()
            messagebox.showinfo("Backup", f"Database backed up to:\n{backup_path}")
            self.log(f"✓ Database backed up to {backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {e}")
    
    def export_memories(self):
        """Export memories to JSON"""
        if not self.memory_system:
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.memory_system.export_all(filepath)
                messagebox.showinfo("Export", f"Memories exported to:\n{filepath}")
                self.log(f"✓ Exported to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def import_memories(self):
        """Import memories from JSON"""
        if not self.memory_system:
            return
        
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                self.memory_system.import_memories(filepath)
                self.refresh_all()
                messagebox.showinfo("Import", "Memories imported successfully!")
                self.log(f"✓ Imported from {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {e}")
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings panel coming soon!")
    
    def log(self, message: str):
        """Log message to status bar"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"[{timestamp}] {message}")
        print(f"[{timestamp}] {message}")


def main():
    root = tk.Tk()
    app = LongTermMemoryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
