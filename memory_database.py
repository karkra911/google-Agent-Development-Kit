"""
Database abstraction layer for AI Agent Long-Term Memory System
Handles SQLite storage, CRUD operations, and advanced querying
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import shutil


class MemoryDatabase:
    """SQLite database manager for long-term memory storage"""
    
    def __init__(self, db_path: str = "memory_database.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database connection and initialize schema"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_indexes()
    
    def create_tables(self):
        """Create tables for all memory types"""
        
        # Episodic Memory Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                duration REAL,
                event_description TEXT NOT NULL,
                context TEXT,
                participants TEXT,
                location TEXT,
                sensory_data TEXT,
                observations TEXT,
                importance_score REAL DEFAULT 50.0,
                emotional_valence REAL DEFAULT 0.0,
                tags TEXT,
                categories TEXT,
                associated_concepts TEXT,
                retrieval_count INTEGER DEFAULT 0,
                last_accessed TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Semantic Memory Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_name TEXT NOT NULL UNIQUE,
                definition TEXT NOT NULL,
                properties TEXT,
                relationships TEXT,
                confidence_score REAL DEFAULT 0.5,
                source TEXT,
                evidence TEXT,
                tags TEXT,
                categories TEXT,
                linked_episodes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Procedural Memory Table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS procedural_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                procedure_name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                purpose TEXT,
                steps TEXT NOT NULL,
                parameters TEXT,
                success_rate REAL DEFAULT 0.0,
                execution_count INTEGER DEFAULT 0,
                average_duration REAL,
                prerequisites TEXT,
                dependencies TEXT,
                tags TEXT,
                categories TEXT,
                last_executed TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def create_indexes(self):
        """Create indexes for faster querying"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memory(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_episodic_importance ON episodic_memory(importance_score)",
            "CREATE INDEX IF NOT EXISTS idx_semantic_concept ON semantic_memory(concept_name)",
            "CREATE INDEX IF NOT EXISTS idx_procedural_name ON procedural_memory(procedure_name)",
        ]
        for index_sql in indexes:
            self.cursor.execute(index_sql)
        self.conn.commit()
    
    # ==================== EPISODIC MEMORY OPERATIONS ====================
    
    def add_episodic_memory(self, memory: Dict[str, Any]) -> int:
        """Add new episodic memory and return its ID"""
        now = datetime.now().isoformat()
        memory.setdefault('created_at', now)
        memory.setdefault('updated_at', now)
        memory.setdefault('retrieval_count', 0)
        
        # Convert lists/dicts to JSON strings
        for field in ['participants', 'sensory_data', 'tags', 'categories', 'associated_concepts']:
            if field in memory and isinstance(memory[field], (list, dict)):
                memory[field] = json.dumps(memory[field])
        
        self.cursor.execute("""
            INSERT INTO episodic_memory 
            (timestamp, duration, event_description, context, participants, location,
             sensory_data, observations, importance_score, emotional_valence,
             tags, categories, associated_concepts, retrieval_count, last_accessed,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.get('timestamp', now),
            memory.get('duration'),
            memory['event_description'],
            memory.get('context'),
            memory.get('participants'),
            memory.get('location'),
            memory.get('sensory_data'),
            memory.get('observations'),
            memory.get('importance_score', 50.0),
            memory.get('emotional_valence', 0.0),
            memory.get('tags'),
            memory.get('categories'),
            memory.get('associated_concepts'),
            memory.get('retrieval_count', 0),
            memory.get('last_accessed'),
            memory['created_at'],
            memory['updated_at']
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_episodic_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve episodic memory by ID"""
        self.cursor.execute("SELECT * FROM episodic_memory WHERE id = ?", (memory_id,))
        row = self.cursor.fetchone()
        if row:
            # Update retrieval count
            self.cursor.execute("""
                UPDATE episodic_memory 
                SET retrieval_count = retrieval_count + 1, last_accessed = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), memory_id))
            self.conn.commit()
            return self._row_to_dict(row)
        return None
    
    def get_all_episodic_memories(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all episodic memories"""
        query = "SELECT * FROM episodic_memory ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"
        self.cursor.execute(query)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def update_episodic_memory(self, memory_id: int, updates: Dict[str, Any]) -> bool:
        """Update episodic memory fields"""
        updates['updated_at'] = datetime.now().isoformat()
        
        # Convert lists/dicts to JSON
        for field in ['participants', 'sensory_data', 'tags', 'categories', 'associated_concepts']:
            if field in updates and isinstance(updates[field], (list, dict)):
                updates[field] = json.dumps(updates[field])
        
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [memory_id]
        
        self.cursor.execute(f"UPDATE episodic_memory SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_episodic_memory(self, memory_id: int) -> bool:
        """Delete episodic memory by ID"""
        self.cursor.execute("DELETE FROM episodic_memory WHERE id = ?", (memory_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ==================== SEMANTIC MEMORY OPERATIONS ====================
    
    def add_semantic_memory(self, memory: Dict[str, Any]) -> int:
        """Add new semantic memory and return its ID"""
        now = datetime.now().isoformat()
        memory.setdefault('created_at', now)
        memory.setdefault('updated_at', now)
        
        # Convert lists/dicts to JSON
        for field in ['properties', 'relationships', 'tags', 'categories', 'linked_episodes']:
            if field in memory and isinstance(memory[field], (list, dict)):
                memory[field] = json.dumps(memory[field])
        
        self.cursor.execute("""
            INSERT INTO semantic_memory 
            (concept_name, definition, properties, relationships, confidence_score,
             source, evidence, tags, categories, linked_episodes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory['concept_name'],
            memory['definition'],
            memory.get('properties'),
            memory.get('relationships'),
            memory.get('confidence_score', 0.5),
            memory.get('source'),
            memory.get('evidence'),
            memory.get('tags'),
            memory.get('categories'),
            memory.get('linked_episodes'),
            memory['created_at'],
            memory['updated_at']
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_semantic_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve semantic memory by ID"""
        self.cursor.execute("SELECT * FROM semantic_memory WHERE id = ?", (memory_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_semantic_memory_by_concept(self, concept_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve semantic memory by concept name"""
        self.cursor.execute("SELECT * FROM semantic_memory WHERE concept_name = ?", (concept_name,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_all_semantic_memories(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all semantic memories"""
        query = "SELECT * FROM semantic_memory ORDER BY concept_name"
        if limit:
            query += f" LIMIT {limit}"
        self.cursor.execute(query)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def update_semantic_memory(self, memory_id: int, updates: Dict[str, Any]) -> bool:
        """Update semantic memory fields"""
        updates['updated_at'] = datetime.now().isoformat()
        
        # Convert lists/dicts to JSON
        for field in ['properties', 'relationships', 'tags', 'categories', 'linked_episodes']:
            if field in updates and isinstance(updates[field], (list, dict)):
                updates[field] = json.dumps(updates[field])
        
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [memory_id]
        
        self.cursor.execute(f"UPDATE semantic_memory SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_semantic_memory(self, memory_id: int) -> bool:
        """Delete semantic memory by ID"""
        self.cursor.execute("DELETE FROM semantic_memory WHERE id = ?", (memory_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ==================== PROCEDURAL MEMORY OPERATIONS ====================
    
    def add_procedural_memory(self, memory: Dict[str, Any]) -> int:
        """Add new procedural memory and return its ID"""
        now = datetime.now().isoformat()
        memory.setdefault('created_at', now)
        memory.setdefault('updated_at', now)
        
        # Convert lists/dicts to JSON
        for field in ['steps', 'parameters', 'prerequisites', 'dependencies', 'tags', 'categories']:
            if field in memory and isinstance(memory[field], (list, dict)):
                memory[field] = json.dumps(memory[field])
        
        self.cursor.execute("""
            INSERT INTO procedural_memory 
            (procedure_name, description, purpose, steps, parameters, success_rate,
             execution_count, average_duration, prerequisites, dependencies,
             tags, categories, last_executed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory['procedure_name'],
            memory['description'],
            memory.get('purpose'),
            memory['steps'],
            memory.get('parameters'),
            memory.get('success_rate', 0.0),
            memory.get('execution_count', 0),
            memory.get('average_duration'),
            memory.get('prerequisites'),
            memory.get('dependencies'),
            memory.get('tags'),
            memory.get('categories'),
            memory.get('last_executed'),
            memory['created_at'],
            memory['updated_at']
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_procedural_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve procedural memory by ID"""
        self.cursor.execute("SELECT * FROM procedural_memory WHERE id = ?", (memory_id,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_procedural_memory_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve procedural memory by procedure name"""
        self.cursor.execute("SELECT * FROM procedural_memory WHERE procedure_name = ?", (name,))
        row = self.cursor.fetchone()
        return self._row_to_dict(row) if row else None
    
    def get_all_procedural_memories(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all procedural memories"""
        query = "SELECT * FROM procedural_memory ORDER BY procedure_name"
        if limit:
            query += f" LIMIT {limit}"
        self.cursor.execute(query)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def update_procedural_memory(self, memory_id: int, updates: Dict[str, Any]) -> bool:
        """Update procedural memory fields"""
        updates['updated_at'] = datetime.now().isoformat()
        
        # Convert lists/dicts to JSON
        for field in ['steps', 'parameters', 'prerequisites', 'dependencies', 'tags', 'categories']:
            if field in updates and isinstance(updates[field], (list, dict)):
                updates[field] = json.dumps(updates[field])
        
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [memory_id]
        
        self.cursor.execute(f"UPDATE procedural_memory SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_procedural_memory(self, memory_id: int) -> bool:
        """Delete procedural memory by ID"""
        self.cursor.execute("DELETE FROM procedural_memory WHERE id = ?", (memory_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ==================== SEARCH & QUERY OPERATIONS ====================
    
    def search_episodic(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Full-text search in episodic memories"""
        self.cursor.execute("""
            SELECT * FROM episodic_memory 
            WHERE event_description LIKE ? OR context LIKE ? OR observations LIKE ?
            ORDER BY importance_score DESC, timestamp DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def search_semantic(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Full-text search in semantic memories"""
        self.cursor.execute("""
            SELECT * FROM semantic_memory 
            WHERE concept_name LIKE ? OR definition LIKE ?
            ORDER BY confidence_score DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', limit))
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def search_procedural(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Full-text search in procedural memories"""
        self.cursor.execute("""
            SELECT * FROM procedural_memory 
            WHERE procedure_name LIKE ? OR description LIKE ?
            ORDER BY success_rate DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', limit))
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    def filter_episodic(self, start_date: Optional[str] = None, end_date: Optional[str] = None,
                       min_importance: Optional[float] = None, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Advanced filtering for episodic memories"""
        query = "SELECT * FROM episodic_memory WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        if min_importance is not None:
            query += " AND importance_score >= ?"
            params.append(min_importance)
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f'%{tag}%')
        
        query += " ORDER BY timestamp DESC"
        self.cursor.execute(query, params)
        return [self._row_to_dict(row) for row in self.cursor.fetchall()]
    
    # ==================== STATISTICS & ANALYTICS ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall memory statistics"""
        stats = {}
        
        # Count totals
        self.cursor.execute("SELECT COUNT(*) FROM episodic_memory")
        stats['episodic_count'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM semantic_memory")
        stats['semantic_count'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM procedural_memory")
        stats['procedural_count'] = self.cursor.fetchone()[0]
        
        stats['total_memories'] = stats['episodic_count'] + stats['semantic_count'] + stats['procedural_count']
        
        # Database size
        if os.path.exists(self.db_path):
            stats['database_size_bytes'] = os.path.getsize(self.db_path)
            stats['database_size_mb'] = round(stats['database_size_bytes'] / (1024 * 1024), 2)
        
        # Episodic stats
        self.cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM episodic_memory")
        oldest, newest = self.cursor.fetchone()
        stats['oldest_episodic'] = oldest
        stats['newest_episodic'] = newest
        
        self.cursor.execute("SELECT AVG(importance_score) FROM episodic_memory")
        avg_importance = self.cursor.fetchone()[0]
        stats['avg_importance'] = round(avg_importance, 2) if avg_importance else 0
        
        # Most retrieved memory
        self.cursor.execute("""
            SELECT id, event_description, retrieval_count 
            FROM episodic_memory 
            ORDER BY retrieval_count DESC LIMIT 1
        """)
        most_retrieved = self.cursor.fetchone()
        if most_retrieved:
            stats['most_retrieved'] = {
                'id': most_retrieved[0],
                'description': most_retrieved[1],
                'count': most_retrieved[2]
            }
        
        return stats
    
    # ==================== UTILITY METHODS ====================
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite Row to dictionary and parse JSON fields"""
        data = dict(row)
        
        # Parse JSON fields
        json_fields = [
            'participants', 'sensory_data', 'tags', 'categories', 'associated_concepts',
            'properties', 'relationships', 'linked_episodes',
            'steps', 'parameters', 'prerequisites', 'dependencies'
        ]
        
        for field in json_fields:
            if field in data and data[field]:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    pass  # Keep as string if not valid JSON
        
        return data
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"memory_database_backup_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    def export_to_json(self, output_path: str):
        """Export all memories to JSON file"""
        data = {
            'episodic': self.get_all_episodic_memories(),
            'semantic': self.get_all_semantic_memories(),
            'procedural': self.get_all_procedural_memories(),
            'statistics': self.get_statistics(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def import_from_json(self, input_path: str):
        """Import memories from JSON file"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Import episodic memories
        for memory in data.get('episodic', []):
            memory.pop('id', None)  # Remove ID to allow auto-increment
            try:
                self.add_episodic_memory(memory)
            except Exception as e:
                print(f"Error importing episodic memory: {e}")
        
        # Import semantic memories
        for memory in data.get('semantic', []):
            memory.pop('id', None)
            try:
                self.add_semantic_memory(memory)
            except Exception as e:
                print(f"Error importing semantic memory: {e}")
        
        # Import procedural memories
        for memory in data.get('procedural', []):
            memory.pop('id', None)
            try:
                self.add_procedural_memory(memory)
            except Exception as e:
                print(f"Error importing procedural memory: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()
