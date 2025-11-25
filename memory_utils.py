"""
Utility functions for AI Agent Long-Term Memory System
Includes similarity calculation, importance scoring, and data validation
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import math


class MemoryUtils:
    """Utility functions for memory operations"""
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using Jaccard similarity
        Returns value between 0 (no similarity) and 1 (identical)
        """
        if not text1 or not text2:
            return 0.0
        
        # Tokenize and normalize
        tokens1 = set(MemoryUtils._tokenize(text1.lower()))
        tokens2 = set(MemoryUtils._tokenize(text2.lower()))
        
        if not tokens1 or not tokens2:
            return 0.0
        
        # Jaccard similarity
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        return len(intersection) / len(union) if union else 0.0
    
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Tokenize text into words"""
        return re.findall(r'\w+', text)
    
    @staticmethod
    def calculate_importance_score(
        emotional_intensity: float = 0.5,
        novelty: float = 0.5,
        relevance: float = 0.5,
        recency: float = 0.5
    ) -> float:
        """
        Calculate importance score based on multiple factors
        All inputs should be between 0 and 1
        Returns score between 0 and 100
        """
        # Weighted combination
        weights = {
            'emotional': 0.3,
            'novelty': 0.25,
            'relevance': 0.25,
            'recency': 0.2
        }
        
        score = (
            emotional_intensity * weights['emotional'] +
            novelty * weights['novelty'] +
            relevance * weights['relevance'] +
            recency * weights['recency']
        )
        
        return min(100.0, max(0.0, score * 100))
    
    @staticmethod
    def apply_temporal_decay(
        original_importance: float,
        timestamp: str,
        decay_rate: float = 0.1,
        half_life_days: int = 30
    ) -> float:
        """
        Apply temporal decay to importance score
        decay_rate: how fast memories decay (0-1)
        half_life_days: days for importance to reduce by half
        """
        try:
            memory_time = datetime.fromisoformat(timestamp)
            days_ago = (datetime.now() - memory_time).days
            
            if days_ago < 0:
                return original_importance
            
            # Exponential decay formula
            decay_factor = math.exp(-decay_rate * days_ago / half_life_days)
            decayed_score = original_importance * decay_factor
            
            return max(0.0, decayed_score)
        except (ValueError, TypeError):
            return original_importance
    
    @staticmethod
    def calculate_retrieval_boost(retrieval_count: int, boost_factor: float = 0.05) -> float:
        """
        Calculate importance boost based on retrieval frequency
        Frequently accessed memories get importance boost
        """
        return min(20.0, retrieval_count * boost_factor)
    
    @staticmethod
    def get_time_period(timestamp: str) -> str:
        """Categorize timestamp into time period (today, this week, this month, etc.)"""
        try:
            memory_time = datetime.fromisoformat(timestamp)
            now = datetime.now()
            delta = now - memory_time
            
            if delta.days == 0:
                return "Today"
            elif delta.days == 1:
                return "Yesterday"
            elif delta.days <= 7:
                return "This Week"
            elif delta.days <= 30:
                return "This Month"
            elif delta.days <= 90:
                return "Last 3 Months"
            elif delta.days <= 365:
                return "This Year"
            else:
                years_ago = delta.days // 365
                return f"{years_ago} Year{'s' if years_ago > 1 else ''} Ago"
        except (ValueError, TypeError):
            return "Unknown"
    
    @staticmethod
    def validate_episodic_memory(memory: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate episodic memory data structure"""
        required_fields = ['event_description', 'timestamp']
        
        for field in required_fields:
            if field not in memory or not memory[field]:
                return False, f"Missing required field: {field}"
        
        # Validate timestamp format
        try:
            datetime.fromisoformat(memory['timestamp'])
        except (ValueError, TypeError):
            return False, "Invalid timestamp format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        
        # Validate importance score
        if 'importance_score' in memory:
            score = memory['importance_score']
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                return False, "Importance score must be between 0 and 100"
        
        # Validate emotional valence
        if 'emotional_valence' in memory:
            valence = memory['emotional_valence']
            if not isinstance(valence, (int, float)) or valence < -1 or valence > 1:
                return False, "Emotional valence must be between -1 and 1"
        
        return True, None
    
    @staticmethod
    def validate_semantic_memory(memory: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate semantic memory data structure"""
        required_fields = ['concept_name', 'definition']
        
        for field in required_fields:
            if field not in memory or not memory[field]:
                return False, f"Missing required field: {field}"
        
        # Validate confidence score
        if 'confidence_score' in memory:
            score = memory['confidence_score']
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                return False, "Confidence score must be between 0 and 1"
        
        return True, None
    
    @staticmethod
    def validate_procedural_memory(memory: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate procedural memory data structure"""
        required_fields = ['procedure_name', 'description', 'steps']
        
        for field in required_fields:
            if field not in memory or not memory[field]:
                return False, f"Missing required field: {field}"
        
        # Validate steps is a list
        if not isinstance(memory['steps'], list):
            return False, "Steps must be a list"
        
        # Validate success rate
        if 'success_rate' in memory:
            rate = memory['success_rate']
            if not isinstance(rate, (int, float)) or rate < 0 or rate > 100:
                return False, "Success rate must be between 0 and 100"
        
        return True, None
    
    @staticmethod
    def format_duration(seconds: Optional[float]) -> str:
        """Format duration in seconds to human-readable string"""
        if seconds is None:
            return "N/A"
        
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text (simple frequency-based approach)"""
        if not text:
            return []
        
        # Tokenize
        tokens = MemoryUtils._tokenize(text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'should', 'could', 'may', 'might', 'must',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their',
            'this', 'that', 'these', 'those', 'and', 'or', 'but', 'if', 'then',
            'in', 'of', 'to', 'for', 'with', 'from', 'by'
        }
        
        # Filter and count
        filtered_tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
        
        # Count frequencies
        freq = {}
        for token in filtered_tokens:
            freq[token] = freq.get(token, 0) + 1
        
        # Sort by frequency and return top N
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_keywords[:max_keywords]]
    
    @staticmethod
    def merge_tags(tags_list: List[List[str]]) -> List[str]:
        """Merge multiple tag lists, removing duplicates"""
        all_tags = set()
        for tags in tags_list:
            if tags:
                all_tags.update(tags)
        return sorted(list(all_tags))
    
    @staticmethod
    def parse_date_range(range_str: str) -> tuple[Optional[str], Optional[str]]:
        """
        Parse date range string into start and end dates
        Accepts: 'today', 'yesterday', 'this_week', 'this_month', 'last_7_days', etc.
        """
        now = datetime.now()
        
        if range_str == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif range_str == 'yesterday':
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(hour=23, minute=59, second=59)
        elif range_str == 'this_week':
            # Start of week (Monday)
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif range_str == 'this_month':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif range_str.startswith('last_') and range_str.endswith('_days'):
            try:
                days = int(range_str.replace('last_', '').replace('_days', ''))
                start = now - timedelta(days=days)
                end = now
            except ValueError:
                return None, None
        else:
            return None, None
        
        return start.isoformat(), end.isoformat()
    
    @staticmethod
    def generate_memory_id(memory_type: str, timestamp: str, description: str) -> str:
        """Generate a unique-ish ID for a memory (for display purposes)"""
        # Simple hash-like ID
        hash_input = f"{memory_type}_{timestamp}_{description}"
        hash_val = hash(hash_input) % 100000
        return f"{memory_type[:3].upper()}{abs(hash_val):05d}"
