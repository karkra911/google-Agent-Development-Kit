
## 🛠️ Technologies Used

- **Python 3.13+** (Agents, Dashboard & Memory System)
- **Google ADK** (Agent Development Kit)
- **SQLite** (Long-term memory database)
- **Tkinter** (GUI interfaces)
- **Local File System** (JSON/CSV) for data storage

## 📦 Repository

This project is available on GitHub: [google-Agent-Development-Kit](https://github.com/karkra911/google-Agent-Development-Kit)

**Branch:** `python-version` (Python implementation)

## ✨ Features

- **Multi-Agent System**: Ingestion, Query, Insight, and Presentation agents
- **Interactive Dashboard**: GUI for managing and running agents
- **Long-Term Memory System**: Persistent storage with SQLite database
- **Memory GUI**: Visual interface for managing agent memories
- **Evaluator Tool**: Test and evaluate agent performance

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/karkra911/google-Agent-Development-Kit.git
   cd google-Agent-Development-Kit
   git checkout python-version
   ```

2. Ensure Python 3.13+ is installed.

3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install google-adk requests
   ```

4. Run the ADK Dashboard to manage agents:
   ```bash
   python adk_dashboard.py
   ```

5. Run the Long-Term Memory GUI:
   ```bash
   python long_term_memory_gui.py
   ```

6. Run the Evaluator GUI:
   ```bash
   python adk_evaluator_gui.py
   ```

## 📁 Project Structure

```
├── code/
│   ├── agents/          # Agent implementations
│   ├── config/          # Configuration files
│   └── shared/          # Shared utilities
├── adk_dashboard.py     # Main dashboard GUI
├── adk_evaluator_gui.py # Agent evaluation tool
├── long_term_memory_gui.py # Memory management GUI
├── long_term_memory.py  # Memory system core
├── memory_database.py   # Database operations
└── memory_retrieval.py  # Memory retrieval logic
```

## 📌 Notes

- Configuration is handled via `code/config/config.json`
- Memory configuration in `memory_config.json`
- Agents operate on local files in `data/input` and `data/output`
- Long-term memory stored in `memory_database.db`
- See `LONG_TERM_MEMORY_README.md` for memory system documentation
