
## 🛠️ Technologies Used

- Python (Agents & Dashboard)
- Local File System (JSON/CSV) for data storage

## 📦 Repository

This project is available on GitHub: [google-Agent-Development-Kit](https://github.com/karkra911/google-Agent-Development-Kit)

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/karkra911/google-Agent-Development-Kit.git
   cd google-Agent-Development-Kit
   ```
2. Ensure Python is installed.
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install google-adk requests
   ```
4. Run `adk_dashboard.py` to manage agents.
   ```bash
   python adk_dashboard.py
   ```
5. Use the Dashboard to run agents.

## 📌 Note

- Configuration is handled via `config/config.json`.
- Agents operate on local files in `data/input` and `data/output`.
