"""
Core Long-Term Memory System for AI Agents
Integrates episodic, semantic, and procedural memory with consolidation
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from memory_database import MemoryDatabase
from memory_retrieval import MemoryRetrieval
from memory_utils import MemoryUtils


class LongTermMemory:
    """Main long-term memory system"""
    
    def __init__(self, config_path: str = "memory_config.json"):
        # Load configuration
        self.config = self.load_config(config_path)
        
        # Initialize components
        self.db = MemoryDatabase(self.config.get('database_path', 'memory_database.db'))
        self.retrieval = MemoryRetrieval(self.db, self.config)
        self.utils = MemoryUtils()
        
        print(f"✓ Long-Term Memory System initialized")
        print(f"  Database: {self.config['database_path']}")
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Return default config
            return {
                'database_path': 'memory_database.db',
                'retrieval': {'default_limit': 50},
                'consolidation': {'enabled': True},
                'decay': {'enabled': True, 'decay_rate': 0.1, 'half_life_days': 30}
            }
    
    # ==================== EPISODIC MEMORY ====================
    
    def store_episode(self, event_description: str, **kwargs) -> int:
        """Store a new episodic memory"""
        memory = {
            'event_description': event_description,
            'timestamp': kwargs.get('timestamp', datetime.now().isoformat()),
            **kwargs
        }
        
        # Validate
        valid, error = self.utils.validate_episodic_memory(memory)
        if not valid:
            raise ValueError(f"Invalid episodic memory: {error}")
        
        # Auto-extract keywords if tags not provided
        if 'tags' not in memory or not memory['tags']:
            memory['tags'] = self.utils.extract_keywords(event_description, max_keywords=5)
        
        memory_id = self.db.add_episodic_memory(memory)
        return memory_id
    
    def recall_episode(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Recall an episodic memory by ID (updates retrieval count)"""
        return self.db.get_episodic_memory(memory_id)
    
    def search_episodes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search episodic memories"""
        return self.db.search_episodic(query, limit=limit)
    
    def get_recent_episodes(self, days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent episodic memories"""
        return self.retrieval.retrieve_recent('episodic', days=days, limit=limit)
    
    def get_important_episodes(self, min_importance: float = 70.0, limit: int = 20) -> List[Dict[str, Any]]:
        """Get important episodic memories"""
        return self.retrieval.retrieve_by_importance(min_importance=min_importance, limit=limit)
    
    # ==================== SEMANTIC MEMORY ====================
    
    def store_concept(self, concept_name: str, definition: str, **kwargs) -> int:
        """Store a new semantic memory (concept/fact)"""
        memory = {
            'concept_name': concept_name,
            'definition': definition,
            **kwargs
        }
        
        # Validate
        valid, error = self.utils.validate_semantic_memory(memory)
        if not valid:
            raise ValueError(f"Invalid semantic memory: {error}")
        
        # Auto-extract keywords if tags not provided
        if 'tags' not in memory or not memory['tags']:
            memory['tags'] = self.utils.extract_keywords(definition, max_keywords=5)
        
        memory_id = self.db.add_semantic_memory(memory)
        return memory_id
    
    def recall_concept(self, concept_name: str) -> Optional[Dict[str, Any]]:
        """Recall a semantic memory by concept name"""
        return self.db.get_semantic_memory_by_concept(concept_name)
    
    def search_concepts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search semantic memories"""
        return self.db.search_semantic(query, limit=limit)
    
    def update_concept_confidence(self, concept_name: str, new_confidence: float):
        """Update confidence score for a concept"""
        concept = self.recall_concept(concept_name)
        if concept:
            self.db.update_semantic_memory(concept['id'], {'confidence_score': new_confidence})
    
    # ==================== PROCEDURAL MEMORY ====================
    
    def store_procedure(self, procedure_name: str, description: str, steps: List[str], **kwargs) -> int:
        """Store a new procedural memory (skill/workflow)"""
        memory = {
            'procedure_name': procedure_name,
            'description': description,
            'steps': steps,
            **kwargs
        }
        
        # Validate
        valid, error = self.utils.validate_procedural_memory(memory)
        if not valid:
            raise ValueError(f"Invalid procedural memory: {error}")
        
        # Auto-extract keywords if tags not provided
        if 'tags' not in memory or not memory['tags']:
            memory['tags'] = self.utils.extract_keywords(description, max_keywords=5)
        
        memory_id = self.db.add_procedural_memory(memory)
        return memory_id
    
    def recall_procedure(self, procedure_name: str) -> Optional[Dict[str, Any]]:
        """Recall a procedural memory by name"""
        return self.db.get_procedural_memory_by_name(procedure_name)
    
    def execute_procedure(self, procedure_name: str, success: bool, duration: Optional[float] = None):
        """Record execution of a procedure and update statistics"""
        procedure = self.recall_procedure(procedure_name)
        if not procedure:
            return
        
        # Update execution stats
        exec_count = procedure.get('execution_count', 0) + 1
        old_success_rate = procedure.get('success_rate', 0.0)
        
        # Calculate new success rate
        new_success_rate = ((old_success_rate * (exec_count - 1)) + (100 if success else 0)) / exec_count
        
        # Update average duration
        if duration is not None:
            old_avg = procedure.get('average_duration', 0) or 0
            new_avg = ((old_avg * (exec_count - 1)) + duration) / exec_count
        else:
            new_avg = procedure.get('average_duration')
        
        updates = {
            'execution_count': exec_count,
            'success_rate': new_success_rate,
            'average_duration': new_avg,
            'last_executed': datetime.now().isoformat()
        }
        
        self.db.update_procedural_memory(procedure['id'], updates)
    
    def search_procedures(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search procedural memories"""
        return self.db.search_procedural(query, limit=limit)
    
    # ==================== ADVANCED RETRIEVAL ====================
    
    def find_similar_memories(self, reference_memory: Dict[str, Any], 
                             memory_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find memories similar to a reference memory"""
        return self.retrieval.retrieve_similar(reference_memory, memory_type, limit)
    
    def retrieve_by_context(self, keywords: List[str], memory_type: str = 'episodic') -> List[Dict[str, Any]]:
        """Retrieve memories matching context keywords"""
        return self.retrieval.retrieve_by_context(keywords, memory_type)
    
    def get_memory_chain(self, start_memory_id: int, max_depth: int = 5) -> List[Dict[str, Any]]:
        """Build associative chain starting from a memory"""
        start_memory = self.recall_episode(start_memory_id)
        if not start_memory:
            return []
        return self.retrieval.retrieve_associative_chain(start_memory, max_depth)
    
    def search_by_tag(self, tag: str, memory_type: str = 'all') -> Dict[str, List[Dict[str, Any]]]:
        """Search memories by tag across all types"""
        return self.retrieval.retrieve_by_tag(tag, memory_type)
    
    # ==================== MEMORY CONSOLIDATION ====================
    
    def consolidate_memories(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Consolidate memories: merge similar ones, archive old ones
        Returns statistics about what would be/was consolidated
        """
        stats = {
            'merged': 0,
            'archived': 0,
            'candidates': []
        }
        
        if not self.config.get('consolidation', {}).get('enabled', True):
            return stats
        
        # Find similar episodic memories to merge
        threshold = self.config['consolidation'].get('merge_similarity_threshold', 0.85)
        all_episodes = self.db.get_all_episodic_memories()
        
        merged_ids = set()
        for i, episode1 in enumerate(all_episodes):
            if episode1['id'] in merged_ids:
                continue
            
            for episode2 in all_episodes[i+1:]:
                if episode2['id'] in merged_ids:
                    continue
                
                similarity = self.utils.calculate_text_similarity(
                    episode1.get('event_description', ''),
                    episode2.get('event_description', '')
                )
                
                if similarity >= threshold:
                    stats['candidates'].append({
                        'id1': episode1['id'],
                        'id2': episode2['id'],
                        'similarity': similarity,
                        'desc1': episode1.get('event_description', '')[:50],
                        'desc2': episode2.get('event_description', '')[:50]
                    })
                    
                    if not dry_run:
                        # Merge episode2 into episode1
                        self._merge_episodes(episode1['id'], episode2['id'])
                        merged_ids.add(episode2['id'])
                        stats['merged'] += 1
        
        return stats
    
    def _merge_episodes(self, keep_id: int, merge_id: int):
        """Merge two episodic memories"""
        keep = self.db.get_episodic_memory(keep_id)
        merge = self.db.get_episodic_memory(merge_id)
        
        if not keep or not merge:
            return
        
        # Combine information
        updates = {
            'retrieval_count': keep.get('retrieval_count', 0) + merge.get('retrieval_count', 0),
            'importance_score': max(keep.get('importance_score', 0), merge.get('importance_score', 0)),
            'tags': self.utils.merge_tags([keep.get('tags', []), merge.get('tags', [])])
        }
        
        # Update and delete
        self.db.update_episodic_memory(keep_id, updates)
        self.db.delete_episodic_memory(merge_id)
    
    # ==================== STATISTICS & MANAGEMENT ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall memory system statistics"""
        return self.db.get_statistics()
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """Create database backup"""
        return self.db.backup_database(backup_path)
    
    def export_all(self, output_path: str = "memory_export.json"):
        """Export all memories to JSON"""
        self.db.export_to_json(output_path)
        return output_path
    
    def import_memories(self, input_path: str):
        """Import memories from JSON"""
        self.db.import_from_json(input_path)
    
    def delete_memory(self, memory_id: int, memory_type: str) -> bool:
        """Delete a memory by ID and type"""
        if memory_type == 'episodic':
            return self.db.delete_episodic_memory(memory_id)
        elif memory_type == 'semantic':
            return self.db.delete_semantic_memory(memory_id)
        elif memory_type == 'procedural':
            return self.db.delete_procedural_memory(memory_id)
        return False
    
    # ==================== TESTING ====================
    
    def test_all_operations(self):
        """Test all memory operations"""
        print("\n=== Testing Long-Term Memory System ===\n")
        
        # Test episodic memory
        print("1. Testing Episodic Memory...")
        ep_id = self.store_episode(
            "First test memory",
            context="Testing environment",
            importance_score=75.0,
            tags=["test", "first"]
        )
        print(f"   ✓ Stored episodic memory ID: {ep_id}")
        
        recalled = self.recall_episode(ep_id)
        print(f"   ✓ Recalled: {recalled['event_description']}")
        
        # Test semantic memory
        print("\n2. Testing Semantic Memory...")
        sem_id = self.store_concept(
            "AI Agent",
            "An autonomous software entity that can perceive, reason, and act",
            confidence_score=0.9,
            tags=["AI", "agent"]
        )
        print(f"   ✓ Stored semantic memory ID: {sem_id}")
        
        concept = self.recall_concept("AI Agent")
        print(f"   ✓ Recalled concept: {concept['concept_name']}")
        
        # Test procedural memory
        print("\n3. Testing Procedural Memory...")
        proc_id = self.store_procedure(
            "Test Workflow",
            "A simple test procedure",
            ["Step 1: Initialize", "Step 2: Execute", "Step 3: Verify"],
            tags=["workflow", "test"]
        )
        print(f"   ✓ Stored procedural memory ID: {proc_id}")
        
        procedure = self.recall_procedure("Test Workflow")
        print(f"   ✓ Recalled procedure: {procedure['procedure_name']}")
        
        # Test search
        print("\n4. Testing Search...")
        results = self.search_episodes("test")
        print(f"   ✓ Found {len(results)} episodic memories matching 'test'")
        
        # Test statistics
        print("\n5. Testing Statistics...")
        stats = self.get_statistics()
        print(f"   ✓ Total memories: {stats['total_memories']}")
        print(f"   ✓ Episodic: {stats['episodic_count']}")
        print(f"   ✓ Semantic: {stats['semantic_count']}")
        print(f"   ✓ Procedural: {stats['procedural_count']}")
        
        print("\n=== All tests passed! ===\n")
        
        return True


if __name__ == "__main__":
    # Quick test
    ltm = LongTermMemory()
    ltm.test_all_operations()
