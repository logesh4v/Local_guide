"""
RAG-based Context Retriever for Local Guide AI.
Retrieves relevant context sections based on user queries with time awareness.
"""
import re
import os
import sys
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class ContextChunk:
    """Represents a chunk of context with metadata."""
    content: str
    section: str
    relevance_score: float
    city: str
    chunk_id: str


class RAGRetriever:
    """RAG-based retriever for context-aware responses."""
    
    def __init__(self):
        """Initialize the RAG retriever."""
        self.context_chunks = {}  # city -> List[ContextChunk]
        self.time_sensitive_keywords = {
            'morning': ['breakfast', 'early', 'dawn', '6am', '7am', '8am', '9am'],
            'afternoon': ['lunch', 'noon', 'midday', '12pm', '1pm', '2pm', '3pm'],
            'evening': ['dinner', 'sunset', 'dusk', '6pm', '7pm', '8pm', '9pm'],
            'night': ['late', 'night', 'after', '10pm', '11pm', 'midnight'],
            'timing': ['when', 'time', 'hours', 'open', 'close', 'schedule']
        }
    
    def load_context_chunks(self, city: str, context_content: str) -> None:
        """
        Load and chunk context content for RAG retrieval.
        
        Args:
            city: City name
            context_content: Full context content
        """
        chunks = self._chunk_context(context_content, city)
        self.context_chunks[city.lower()] = chunks
    
    def _chunk_context(self, content: str, city: str) -> List[ContextChunk]:
        """
        Split context into meaningful chunks for retrieval.
        
        Args:
            content: Full context content
            city: City name
            
        Returns:
            List of context chunks
        """
        chunks = []
        
        # Split by main sections (##)
        sections = re.split(r'\n## ', content)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Extract section title
            lines = section.split('\n')
            section_title = lines[0].replace('#', '').strip()
            
            # Further split by subsections (###)
            subsections = re.split(r'\n### ', section)
            
            for j, subsection in enumerate(subsections):
                if not subsection.strip():
                    continue
                
                # Create chunk
                chunk = ContextChunk(
                    content=subsection.strip(),
                    section=section_title,
                    relevance_score=0.0,
                    city=city.lower(),
                    chunk_id=f"{city.lower()}_{i}_{j}"
                )
                chunks.append(chunk)
        
        return chunks
    
    def retrieve_relevant_context(self, query: str, city: str, top_k: int = 5) -> List[ContextChunk]:
        """
        Retrieve most relevant context chunks for a query.
        
        Args:
            query: User query
            city: Selected city
            top_k: Number of top chunks to return
            
        Returns:
            List of relevant context chunks
        """
        city_lower = city.lower()
        if city_lower not in self.context_chunks:
            return []
        
        chunks = self.context_chunks[city_lower]
        
        # Score each chunk
        scored_chunks = []
        for chunk in chunks:
            score = self._calculate_relevance_score(query, chunk)
            chunk.relevance_score = score
            scored_chunks.append(chunk)
        
        # Sort by relevance score and return top_k
        scored_chunks.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored_chunks[:top_k]
    
    def _calculate_relevance_score(self, query: str, chunk: ContextChunk) -> float:
        """
        Calculate relevance score between query and chunk.
        
        Args:
            query: User query
            chunk: Context chunk
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        query_lower = query.lower()
        content_lower = chunk.content.lower()
        section_lower = chunk.section.lower()
        
        score = 0.0
        
        # Exact word matches in content
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        content_words = set(re.findall(r'\b\w+\b', content_lower))
        
        # Calculate word overlap
        overlap = query_words.intersection(content_words)
        if query_words:
            word_overlap_score = len(overlap) / len(query_words)
            score += word_overlap_score * 0.6
        
        # Section title relevance
        section_words = set(re.findall(r'\b\w+\b', section_lower))
        section_overlap = query_words.intersection(section_words)
        if query_words:
            section_score = len(section_overlap) / len(query_words)
            score += section_score * 0.3
        
        # Time-sensitive boost
        time_boost = self._get_time_sensitivity_boost(query_lower, content_lower)
        score += time_boost * 0.1
        
        return min(score, 1.0)
    
    def _get_time_sensitivity_boost(self, query: str, content: str) -> float:
        """
        Calculate time sensitivity boost based on current time and query.
        
        Args:
            query: User query (lowercase)
            content: Chunk content (lowercase)
            
        Returns:
            Time sensitivity boost (0.0 to 1.0)
        """
        current_hour = datetime.now().hour
        
        # Determine current time period
        if 6 <= current_hour < 12:
            current_period = 'morning'
        elif 12 <= current_hour < 17:
            current_period = 'afternoon'
        elif 17 <= current_hour < 22:
            current_period = 'evening'
        else:
            current_period = 'night'
        
        boost = 0.0
        
        # Check if query contains time-sensitive keywords
        for period, keywords in self.time_sensitive_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    # Boost if it matches current time period
                    if period == current_period:
                        boost += 0.3
                    # Check if content is relevant to this time period
                    if keyword in content or any(kw in content for kw in keywords):
                        boost += 0.2
                    break
        
        # Special boost for timing-related queries
        if any(kw in query for kw in self.time_sensitive_keywords['timing']):
            if any(time_word in content for time_word in ['am', 'pm', 'hour', 'time', 'open', 'close']):
                boost += 0.4
        
        return min(boost, 1.0)
    
    def get_time_context(self) -> str:
        """
        Get current time context for responses.
        
        Returns:
            Time context string
        """
        now = datetime.now()
        current_hour = now.hour
        
        # Determine time period and appropriate context
        if 6 <= current_hour < 12:
            period = "morning"
            context = "It's morning now, so breakfast places and early activities are most relevant."
        elif 12 <= current_hour < 17:
            period = "afternoon"
            context = "It's afternoon now, so lunch options and midday activities are most suitable."
        elif 17 <= current_hour < 22:
            period = "evening"
            context = "It's evening now, so dinner places and evening activities are ideal."
        else:
            period = "night"
            context = "It's late night now, so options may be limited. Most places close early."
        
        return f"Current time: {now.strftime('%I:%M %p')} ({period}). {context}"
    
    def build_rag_context(self, query: str, city: str) -> str:
        """
        Build RAG-enhanced context for the query.
        
        Args:
            query: User query
            city: Selected city
            
        Returns:
            Enhanced context string
        """
        # Get relevant chunks
        relevant_chunks = self.retrieve_relevant_context(query, city, top_k=3)
        
        if not relevant_chunks:
            return ""
        
        # Build context
        context_parts = []
        
        # Add time context
        time_context = self.get_time_context()
        context_parts.append(f"TIME CONTEXT: {time_context}")
        
        # Add relevant chunks
        context_parts.append("RELEVANT LOCAL INFORMATION:")
        
        for i, chunk in enumerate(relevant_chunks, 1):
            context_parts.append(f"\n{i}. {chunk.section}:")
            context_parts.append(chunk.content)
        
        return "\n".join(context_parts)
    
    def get_retrieval_stats(self, city: str) -> Dict:
        """
        Get statistics about loaded context chunks.
        
        Args:
            city: City name
            
        Returns:
            Statistics dictionary
        """
        city_lower = city.lower()
        if city_lower not in self.context_chunks:
            return {"total_chunks": 0, "sections": []}
        
        chunks = self.context_chunks[city_lower]
        sections = list(set(chunk.section for chunk in chunks))
        
        return {
            "total_chunks": len(chunks),
            "sections": sections,
            "city": city
        }