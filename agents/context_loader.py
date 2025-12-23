"""
Context Loader Agent for Local Guide AI.
Responsible for loading and managing city-specific context files.
"""
import os
import sys
from datetime import datetime
from typing import List, Optional
from strands import Agent

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import CityContext


class ContextLoaderAgent:
    """Agent responsible for loading city-specific context files."""
    
    def __init__(self, context_dir: str = "context"):
        """
        Initialize the Context Loader Agent.
        
        Args:
            context_dir: Directory containing context files
        """
        self.context_dir = context_dir
        self.available_cities = ['madurai', 'dindigul']
        self.current_context: Optional[CityContext] = None
    
    def get_available_cities(self) -> List[str]:
        """
        Get list of available cities.
        
        Returns:
            List of available city names
        """
        return [city.title() for city in self.available_cities]
    
    def validate_city_selection(self, city: str) -> bool:
        """
        Validate if the selected city is supported.
        
        Args:
            city: City name to validate
            
        Returns:
            True if city is supported, False otherwise
        """
        return city.lower() in self.available_cities
    
    def load_city_context(self, city: str) -> CityContext:
        """
        Load context file for the specified city.
        
        Args:
            city: Name of the city to load context for
            
        Returns:
            CityContext object with loaded content
            
        Raises:
            ValueError: If city is not supported
            FileNotFoundError: If context file doesn't exist
            IOError: If context file cannot be read
        """
        if not self.validate_city_selection(city):
            raise ValueError(f"City '{city}' is not supported. Available cities: {self.get_available_cities()}")
        
        city_lower = city.lower()
        file_path = os.path.join(self.context_dir, f"{city_lower}_context.md")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Context file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                raise IOError(f"Context file is empty: {file_path}")
            
            context = CityContext(
                city_name=city_lower,
                context_content=content,
                file_path=file_path,
                last_loaded=datetime.now()
            )
            
            # Store current context and ensure isolation
            self.current_context = context
            
            return context
            
        except Exception as e:
            raise IOError(f"Failed to read context file {file_path}: {str(e)}")
    
    def get_current_context(self) -> Optional[CityContext]:
        """
        Get the currently loaded context.
        
        Returns:
            Current CityContext or None if no context is loaded
        """
        return self.current_context
    
    def clear_context(self) -> None:
        """Clear the currently loaded context."""
        self.current_context = None
    
    def switch_city_context(self, new_city: str) -> CityContext:
        """
        Switch to a different city's context, ensuring complete isolation.
        
        Args:
            new_city: Name of the new city to switch to
            
        Returns:
            New CityContext object
        """
        # Clear current context to ensure isolation
        self.clear_context()
        
        # Load new context
        return self.load_city_context(new_city)
    
    def is_context_loaded(self) -> bool:
        """
        Check if a context is currently loaded.
        
        Returns:
            True if context is loaded and valid, False otherwise
        """
        return (
            self.current_context is not None and 
            self.current_context.is_valid()
        )
    
    def get_context_summary(self) -> str:
        """
        Get a summary of the currently loaded context.
        
        Returns:
            Summary string or empty string if no context loaded
        """
        if not self.is_context_loaded():
            return ""
        
        context = self.current_context
        return f"Loaded context for {context.city_name.title()} from {context.file_path} at {context.last_loaded}"
    
    def validate_context_isolation(self, city: str) -> bool:
        """
        Validate that the loaded context contains only the specified city's information.
        
        Args:
            city: City name to validate against
            
        Returns:
            True if context is properly isolated, False otherwise
        """
        if not self.is_context_loaded():
            return False
        
        context = self.current_context
        city_lower = city.lower()
        
        # Check that context is for the correct city
        if context.city_name != city_lower:
            return False
        
        # Check that context contains city-specific information
        content_lower = context.context_content.lower()
        if city_lower not in content_lower:
            return False
        
        # Check that context doesn't contain other city information
        other_cities = [c for c in self.available_cities if c != city_lower]
        for other_city in other_cities:
            # Allow mentions in comparative context but not as primary content
            if content_lower.count(other_city) > content_lower.count(city_lower) / 10:
                return False
        
        return True