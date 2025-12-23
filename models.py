"""
Core data models for Local Guide AI application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Tuple
import hashlib


@dataclass
class CityContext:
    """Model for city-specific context data."""
    city_name: str
    context_content: str
    file_path: str
    last_loaded: datetime
    
    def is_valid(self) -> bool:
        """Check if the context is valid."""
        return (
            bool(self.city_name) and 
            bool(self.context_content) and 
            bool(self.file_path) and
            self.city_name.lower() in ['madurai', 'dindigul']
        )
    
    def get_content_hash(self) -> str:
        """Get hash of the context content for change detection."""
        return hashlib.md5(self.context_content.encode()).hexdigest()


@dataclass
class Query:
    """Model for user queries."""
    text: str
    city: str
    timestamp: datetime
    is_valid: bool
    validation_reason: Optional[str] = None
    
    def get_supported_topics(self) -> List[str]:
        """Get list of supported topics."""
        return ['food', 'transport', 'slang', 'safety', 'lifestyle']
    
    def is_empty(self) -> bool:
        """Check if query is empty or whitespace only."""
        return not self.text or self.text.strip() == ""


@dataclass
class Response:
    """Model for AI responses."""
    text: str
    is_refusal: bool
    refusal_reason: Optional[str] = None
    source_context: str = ""
    validation_passed: bool = True
    
    def is_standardized_refusal(self) -> bool:
        """Check if response uses standardized refusal phrases."""
        if not self.is_refusal:
            return False
            
        standardized_phrases = [
            "This isn't covered in my local context.",
            "I don't have enough local data to answer that.",
            "My knowledge is limited to what's in the context file."
        ]
        
        return any(phrase in self.text for phrase in standardized_phrases)


@dataclass
class AppState:
    """Model for application state."""
    selected_city: Optional[str] = None
    loaded_context: Optional[CityContext] = None
    conversation_history: List[Tuple[Query, Response]] = None
    
    def __post_init__(self):
        """Initialize conversation history if not provided."""
        if self.conversation_history is None:
            self.conversation_history = []
    
    def reset_city_selection(self) -> None:
        """Reset city selection and clear context."""
        self.selected_city = None
        self.loaded_context = None
        self.conversation_history.clear()
    
    def add_interaction(self, query: Query, response: Response) -> None:
        """Add a query-response interaction to history."""
        self.conversation_history.append((query, response))
    
    def get_available_cities(self) -> List[str]:
        """Get list of available cities."""
        return ['Madurai', 'Dindigul']
    
    def is_city_selected(self) -> bool:
        """Check if a city is currently selected."""
        return self.selected_city is not None
    
    def is_context_loaded(self) -> bool:
        """Check if context is loaded for selected city."""
        return self.loaded_context is not None and self.loaded_context.is_valid()