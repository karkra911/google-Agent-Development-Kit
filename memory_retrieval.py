"""
Advanced retrieval mechanisms for AI Agent Long-Term Memory System
Implements context-aware, temporal, and similarity-based memory retrieval
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from memory_database import MemoryDatabase
from memory_utils import MemoryUtils


class MemoryRetrieval:
    """Advanced memory retrieval with multiple search strategies"""
    
    def __init__(self, database: MemoryDatabase, config: Dict[str, Any]):
        self.db = database
        self.config = config
        self.utils = MemoryUtils()
    
    def retrieve_by_context(self, context_keywords: List[str], 
                           memory_type: str = 'episodic',
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve memories matching context keywords
        Uses importance-weighted ranking
        """
        all_memories = []
        
        if memory_type == 'episodic':
            all_memories = self.db.get_all_episodic_memories()
        elif memory_type == 'semantic':
            all_memories = self.db.get_all_semantic_memories()
        elif memory_type == 'procedural':
            all_memories = self.db.get_all_procedural_memories()
        
        # Score each memory based on context match
        scored_memories = []
        for memory in all_memories:
            score = self._calculate_context_score(memory, context_keywords, memory_type)
            if score > 0:
                memory['context_score'] = score
                scored_memories.append(memory)
        
        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x['context_score'], reverse=True)
        return scored_memories[:limit]
    
    def retrieve_by_time_period(self, period: str, memory_type: str = 'episodic') -> List[Dict[str, Any]]:
        """
        Retrieve memories from specific time period
        period: 'today', 'yesterday', 'this_week', 'this_month', 'last_7_days', etc.
        """
        start_date, end_date = self.utils.parse_date_range(period)
        
        if not start_date or not end_date:
            return []
        
        if memory_type == 'episodic':
            return self.db.filter_episodic(start_date=start_date, end_date=end_date)
        else:
            # For non-episodic, we'll filter after retrieval
            if memory_type == 'semantic':
                memories = self.db.get_all_semantic_memories()
            else:
                memories = self.db.get_all_procedural_memories()
            
            return [m for m in memories 
                   if start_date <= m.get('created_at', '') <= end_date]
    
    def retrieve_similar(self, reference_memory: Dict[str, Any], 
                        memory_type: str = 'episodic',
                        limit: int = 5) -> List[Dict[str, Any]]:
        """Find memories similar to a reference memory"""
        all_memories = []
        
        if memory_type == 'episodic':
            all_memories = self.db.get_all_episodic_memories()
            ref_text = reference_memory.get('event_description', '')
        elif memory_type == 'semantic':
            all_memories = self.db.get_all_semantic_memories()
            ref_text = reference_memory.get('definition', '')
        elif memory_type == 'procedural':
            all_memories = self.db.get_all_procedural_memories()
            ref_text = reference_memory.get('description', '')
        else:
            return []
        
        # Calculate similarity for each memory
        similarities = []
        for memory in all_memories:
            # Skip the reference memory itself
            if memory.get('id') == reference_memory.get('id'):
                continue
            
            if memory_type == 'episodic':
                compare_text = memory.get('event_description', '')
            elif memory_type == 'semantic':
                compare_text = memory.get('definition', '')
            else:
                compare_text = memory.get('description', '')
            
            similarity = self.utils.calculate_text_similarity(ref_text, compare_text)
            
            if similarity > self.config.get('retrieval', {}).get('similarity_threshold', 0.3):
                memory['similarity_score'] = similarity
                similarities.append(memory)
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:limit]
    
    def retrieve_by_importance(self, min_importance: float = 70.0,
                              apply_decay: bool = True,
                              limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve episodic memories above importance threshold"""
        memories = self.db.get_all_episodic_memories()
        
        important_memories = []
        for memory in memories:
            importance = memory.get('importance_score', 0)
            
            # Apply temporal decay if enabled
            if apply_decay and self.config.get('decay', {}).get('enabled', True):
                importance = self.utils.apply_temporal_decay(
                    importance,
                    memory.get('timestamp', ''),
                    decay_rate=self.config['decay'].get('decay_rate', 0.1),
                    half_life_days=self.config['decay'].get('half_life_days', 30)
                )
                
                # Add retrieval boost
                retrieval_boost = self.utils.calculate_retrieval_boost(
                    memory.get('retrieval_count', 0),
                    boost_factor=self.config['importance_calculation'].get('retrieval_boost_factor', 0.05)
                )
                importance += retrieval_boost
            
            if importance >= min_importance:
                memory['adjusted_importance'] = importance
                important_memories.append(memory)
        
        # Sort by adjusted importance
        important_memories.sort(key=lambda x: x.get('adjusted_importance', 0), reverse=True)
        return important_memories[:limit]
    
    def retrieve_associative_chain(self, start_memory: Dict[str, Any],
                                   max_depth: int = 5) -> List[Dict[str, Any]]:
        """
        Follow associative links to build a chain of related memories
        Uses tags and concepts to link memories
        """
        chain = [start_memory]
        visited_ids = {start_memory.get('id')}
        
        current_memory = start_memory
        for _ in range(max_depth):
            # Get associated concepts or tags
            associated = current_memory.get('associated_concepts', []) or []
            tags = current_memory.get('tags', []) or []
            
            search_terms = associated + tags
            if not search_terms:
                break
            
            # Find next memory with matching concepts/tags
            next_memory = None
            for term in search_terms[:3]:  # Check top 3 terms
                results = self.db.search_episodic(term, limit=5)
                for result in results:
                    if result.get('id') not in visited_ids:
                        next_memory = result
                        break
                if next_memory:
                    break
            
            if not next_memory:
                break
            
            chain.append(next_memory)
            visited_ids.add(next_memory.get('id'))
            current_memory = next_memory
        
        return chain
    
    def retrieve_recent(self, memory_type: str = 'episodic',
                       days: int = 7, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent memories from last N days"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        end_date = datetime.now().isoformat()
        
        if memory_type == 'episodic':
            return self.db.filter_episodic(start_date=start_date, end_date=end_date)
        else:
            # Filter by created_at for other types
            if memory_type == 'semantic':
                memories = self.db.get_all_semantic_memories()
            else:
                memories = self.db.get_all_procedural_memories()
            
            recent = [m for m in memories 
                     if m.get('created_at', '') >= start_date]
            recent.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return recent[:limit]
    
    def retrieve_by_tag(self, tag: str, memory_type: str = 'all',
                       limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """Retrieve memories with specific tag across all types"""
        results = {
            'episodic': [],
            'semantic': [],
            'procedural': []
        }
        
        if memory_type in ['all', 'episodic']:
            all_episodic = self.db.get_all_episodic_memories()
            results['episodic'] = [
                m for m in all_episodic 
                if tag.lower() in [t.lower() for t in m.get('tags', []) or []]
            ][:limit]
        
        if memory_type in ['all', 'semantic']:
            all_semantic = self.db.get_all_semantic_memories()
            results['semantic'] = [
                m for m in all_semantic 
                if tag.lower() in [t.lower() for t in m.get('tags', []) or []]
            ][:limit]
        
        if memory_type in ['all', 'procedural']:
            all_procedural = self.db.get_all_procedural_memories()
            results['procedural'] = [
                m for m in all_procedural 
                if tag.lower() in [t.lower() for t in m.get('tags', []) or []]
            ][:limit]
        
        return results
    
    def _calculate_context_score(self, memory: Dict[str, Any], 
                                 keywords: List[str], 
                                 memory_type: str) -> float:
        """Calculate how well a memory matches context keywords"""
        # Get searchable text based on memory type
        if memory_type == 'episodic':
            text = ' '.join([
                memory.get('event_description', ''),
                memory.get('context', ''),
                memory.get('observations', '')
            ])
        elif memory_type == 'semantic':
            text = ' '.join([
                memory.get('concept_name', ''),
                memory.get('definition', '')
            ])
        else:  # procedural
            text = ' '.join([
                memory.get('procedure_name', ''),
                memory.get('description', '')
            ])
        
        text = text.lower()
        
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword.lower() in text)
        
        # Normalize by number of keywords
        base_score = matches / len(keywords) if keywords else 0
        
        # Weight by importance/confidence if available
        if memory_type == 'episodic':
            weight = memory.get('importance_score', 50) / 100
        elif memory_type == 'semantic':
            weight = memory.get('confidence_score', 0.5)
        else:
            weight = memory.get('success_rate', 0) / 100
        
        return base_score * weight
