# AI Agent Long-Term Memory System

A comprehensive long-term memory system for AI agents featuring episodic, semantic, and procedural memory with a modern GUI interface.

## 🚀 Quick Start

### Running the GUI

```powershell
python long_term_memory_gui.py
```

### Running Core Tests

```powershell
python long_term_memory.py
```

## 📋 Features

### Three Memory Types

- **Episodic Memory**: Stores experiences and events with context
- **Semantic Memory**: Stores facts, concepts, and knowledge
- **Procedural Memory**: Stores skills, workflows, and procedures

### GUI Capabilities

- ✅ Memory browser with tabbed interface
- ✅ Complete parameter visibility for all memories
- ✅ Statistics dashboard
- ✅ Search and filter
- ✅ Add/Edit/Delete operations
- ✅ Import/Export to JSON
- ✅ Database backup
- ✅ Dark theme UI

## 📊 Memory Parameters

### Episodic Memory
- Timestamp, Duration, Event Description
- Context, Participants, Location
- Sensory Data, Observations
- Importance Score (0-100)
- Emotional Valence (-1 to +1)
- Tags, Categories, Associated Concepts
- Retrieval Count, Timestamps

### Semantic Memory
- Concept Name, Definition
- Properties, Relationships
- Confidence Score (0-1)
- Source, Evidence
- Tags, Categories, Linked Episodes
- Timestamps

### Procedural Memory
- Procedure Name, Description
- Steps, Parameters
- Success Rate, Execution Count
- Average Duration
- Prerequisites, Dependencies
- Tags, Categories, Timestamps

## 🗂️ Files

- `long_term_memory_gui.py` - Main GUI application
- `long_term_memory.py` - Core memory engine
- `memory_database.py` - SQLite database layer
- `memory_retrieval.py` - Advanced retrieval mechanisms
- `memory_utils.py` - Utility functions
- `memory_config.json` - Configuration settings
- `memory_database.db` - SQLite database (created on first run)

## 🎯 Usage Examples

### Storing Memories

```python
from long_term_memory import LongTermMemory

ltm = LongTermMemory()

# Store episodic memory
ltm.store_episode(
    "AI agent learned to play chess",
    context="Training environment",
    importance_score=85.0,
    tags=["learning", "chess", "achievement"]
)

# Store semantic memory
ltm.store_concept(
    "Policy Gradient",
    "Reinforcement learning algorithm that optimizes policy directly",
    confidence_score=0.9,
    tags=["RL", "algorithm"]
)

# Store procedural memory
ltm.store_procedure(
    "Deploy Model",
    "Deploy trained model to production",
    steps=["Export model", "Test locally", "Upload to server", "Verify"],
    tags=["deployment", "workflow"]
)
```

### Retrieving Memories

```python
# Search
results = ltm.search_episodes("chess")

# Get recent memories
recent = ltm.get_recent_episodes(days=7)

# Get important memories
important = ltm.get_important_episodes(min_importance=70.0)

# Find similar memories
similar = ltm.find_similar_memories(some_memory, 'episodic')
```

## ⚙️ Configuration

Edit `memory_config.json` to customize:

- Database path
- Retrieval parameters
- Consolidation settings
- Decay rates
- GUI preferences

## 📦 Requirements

- Python 3.7+
- tkinter (usually included with Python)
- Standard library only (sqlite3, json, datetime, threading)

## 🧪 Testing

The system includes comprehensive tests:

```
✓ Episodic memory storage and retrieval
✓ Semantic memory storage and retrieval
✓ Procedural memory storage and retrieval
✓ Search functionality
✓ Statistics generation
```

All tests pass successfully.

## 🎨 GUI Features

- **Dark Theme**: Professional dark color scheme
- **Color Coding**: Episodic (Blue), Semantic (Purple), Procedural (Red)
- **Real-time Updates**: Statistics and memory lists update automatically
- **Full Parameter Display**: All memory fields visible in details panel
- **Intuitive Controls**: Easy-to-use buttons and dialogs

## 📝 License

Part of the Google Agent Development Kit project.

## 🤝 Integration

To integrate with existing agent systems, use the `LongTermMemory` class:

```python
from long_term_memory import LongTermMemory

# Initialize
memory = LongTermMemory(config_path="memory_config.json")

# Use in your agent
# ... agent code ...
```

---

**Status**: ✅ Complete and Ready for Use

For detailed documentation, see the walkthrough.md file.
