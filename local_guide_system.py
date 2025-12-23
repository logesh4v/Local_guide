"""
Main Local Guide System - Coordinates all agents and manages the processing pipeline.
"""
import os
import sys
from typing import Optional, Tuple
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Query, Response, AppState, CityContext
from agents.context_loader import ContextLoaderAgent
from agents.query_validator import QueryValidationAgent
from agents.local_guide_agent import LocalGuideAgent
from agents.guard_agent import GuardAgent
from refusal_handler import RefusalHandler, RefusalReason


class LocalGuideSystem:
    """Main system that coordinates all agents for local guide functionality."""
    
    def __init__(self):
        """Initialize the Local Guide System with all agents."""
        self.context_loader = ContextLoaderAgent()
        self.query_validator = QueryValidationAgent()
        self.local_guide = LocalGuideAgent()
        self.guard_agent = GuardAgent()
        self.refusal_handler = RefusalHandler()
        
        self.app_state = AppState()
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the system and test connections.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Test model connection
            if not self.local_guide.test_model_connection():
                print("Warning: Model connection test failed. AWS credentials may not be configured.")
                # Continue anyway for testing purposes
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            print(f"System initialization failed: {str(e)}")
            return False
    
    def select_city(self, city: str) -> Tuple[bool, str]:
        """
        Select a city and load its context.
        
        Args:
            city: Name of the city to select
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Validate city selection
            if not self.context_loader.validate_city_selection(city):
                available_cities = self.context_loader.get_available_cities()
                return False, f"Invalid city '{city}'. Available cities: {', '.join(available_cities)}"
            
            # Load city context
            context = self.context_loader.load_city_context(city)
            
            # Update app state
            self.app_state.selected_city = city.title()
            self.app_state.loaded_context = context
            
            return True, f"Successfully loaded context for {city.title()}"
            
        except Exception as e:
            return False, f"Failed to select city: {str(e)}"
    
    def process_query(self, query_text: str) -> Response:
        """
        Process a user query through the complete pipeline.
        
        Args:
            query_text: User's query text
            
        Returns:
            Response object with the result
        """
        # Check if system is ready
        if not self.is_initialized:
            return self._create_error_response("System not initialized")
        
        if not self.app_state.is_city_selected():
            return self._create_error_response("No city selected. Please select a city first.")
        
        if not self.app_state.is_context_loaded():
            return self._create_error_response("City context not loaded. Please select a city.")
        
        try:
            # Step 1: Create and validate query
            query = self.query_validator.create_validation_response(
                query_text, 
                self.app_state.selected_city
            )
            
            # Step 2: Check query validation
            if not query.is_valid:
                response = Response(
                    text=query.validation_reason,
                    is_refusal=True,
                    refusal_reason="Query validation failed",
                    source_context=f"{self.app_state.selected_city} context"
                )
                self.app_state.add_interaction(query, response)
                return response
            
            # Step 3: Generate response using Local Guide Agent with RAG
            context_content = self.app_state.loaded_context.context_content
            response = self.local_guide.create_response_object(
                query.text,
                context_content,
                self.app_state.selected_city
            )
            
            # Step 4: Validate response with Guard Agent
            validated_response = self.guard_agent.validate_response_object(
                response,
                context_content
            )
            
            # Step 5: Ensure standardized refusal format if needed
            if validated_response.is_refusal:
                validated_response.text = self.refusal_handler.ensure_standardized_refusal(
                    validated_response.text,
                    RefusalReason.INSUFFICIENT_DATA
                )
            
            # Step 6: Add to conversation history
            self.app_state.add_interaction(query, validated_response)
            
            return validated_response
            
        except Exception as e:
            error_response = self._create_error_response(f"Processing error: {str(e)}")
            return error_response
    
    def get_available_cities(self) -> list:
        """
        Get list of available cities.
        
        Returns:
            List of available city names
        """
        return self.context_loader.get_available_cities()
    
    def get_current_city(self) -> Optional[str]:
        """
        Get currently selected city.
        
        Returns:
            Current city name or None if no city selected
        """
        return self.app_state.selected_city
    
    def get_system_status(self) -> dict:
        """
        Get current system status.
        
        Returns:
            Dictionary with system status information
        """
        return {
            'initialized': self.is_initialized,
            'selected_city': self.app_state.selected_city,
            'context_loaded': self.app_state.is_context_loaded(),
            'conversation_length': len(self.app_state.conversation_history),
            'model_info': self.local_guide.get_model_info(),
            'available_cities': self.get_available_cities()
        }
    
    def reset_session(self) -> None:
        """Reset the current session and clear state."""
        self.app_state.reset_city_selection()
        self.context_loader.clear_context()
    
    def switch_city(self, new_city: str) -> Tuple[bool, str]:
        """
        Switch to a different city.
        
        Args:
            new_city: Name of the new city to switch to
            
        Returns:
            Tuple of (success, message)
        """
        # Clear current state
        self.reset_session()
        
        # Select new city
        return self.select_city(new_city)
    
    def get_conversation_history(self) -> list:
        """
        Get conversation history for current session.
        
        Returns:
            List of (query, response) tuples
        """
        return self.app_state.conversation_history.copy()
    
    def get_context_summary(self) -> str:
        """
        Get summary of currently loaded context.
        
        Returns:
            Context summary string
        """
        if not self.app_state.is_context_loaded():
            return "No context loaded"
        
        return self.context_loader.get_context_summary()
    
    def validate_system_health(self) -> dict:
        """
        Validate system health and component status.
        
        Returns:
            Dictionary with health check results
        """
        health = {
            'overall_status': 'healthy',
            'components': {},
            'issues': []
        }
        
        # Check Context Loader
        try:
            cities = self.context_loader.get_available_cities()
            health['components']['context_loader'] = 'healthy' if cities else 'warning'
            if not cities:
                health['issues'].append('No cities available in context loader')
        except Exception as e:
            health['components']['context_loader'] = 'error'
            health['issues'].append(f'Context loader error: {str(e)}')
        
        # Check Query Validator
        try:
            topics = self.query_validator.get_supported_topics()
            health['components']['query_validator'] = 'healthy' if topics else 'error'
        except Exception as e:
            health['components']['query_validator'] = 'error'
            health['issues'].append(f'Query validator error: {str(e)}')
        
        # Check Local Guide Agent
        try:
            model_info = self.local_guide.get_model_info()
            connection_ok = self.local_guide.test_model_connection()
            health['components']['local_guide'] = 'healthy' if connection_ok else 'warning'
            if not connection_ok:
                health['issues'].append('Local guide agent connection issue (AWS credentials may be missing)')
        except Exception as e:
            health['components']['local_guide'] = 'error'
            health['issues'].append(f'Local guide agent error: {str(e)}')
        
        # Check Guard Agent
        try:
            refusals = self.guard_agent.standardized_refusals
            health['components']['guard_agent'] = 'healthy' if refusals else 'error'
        except Exception as e:
            health['components']['guard_agent'] = 'error'
            health['issues'].append(f'Guard agent error: {str(e)}')
        
        # Determine overall status
        if any(status == 'error' for status in health['components'].values()):
            health['overall_status'] = 'error'
        elif any(status == 'warning' for status in health['components'].values()):
            health['overall_status'] = 'warning'
        
        return health
    
    def _create_error_response(self, error_message: str) -> Response:
        """
        Create an error response.
        
        Args:
            error_message: Error message
            
        Returns:
            Response object with error information
        """
        return Response(
            text=self.refusal_handler.get_refusal_by_reason(RefusalReason.GENERAL_LIMITATION),
            is_refusal=True,
            refusal_reason=error_message,
            source_context="system",
            validation_passed=False
        )
    
    def get_usage_statistics(self) -> dict:
        """
        Get usage statistics for the current session.
        
        Returns:
            Dictionary with usage statistics
        """
        history = self.app_state.conversation_history
        
        if not history:
            return {
                'total_queries': 0,
                'successful_responses': 0,
                'refusal_responses': 0,
                'refusal_rate': 0.0
            }
        
        total_queries = len(history)
        refusal_responses = sum(1 for _, response in history if response.is_refusal)
        successful_responses = total_queries - refusal_responses
        
        return {
            'total_queries': total_queries,
            'successful_responses': successful_responses,
            'refusal_responses': refusal_responses,
            'refusal_rate': refusal_responses / total_queries if total_queries > 0 else 0.0,
            'current_city': self.app_state.selected_city,
            'session_start': history[0][0].timestamp if history else None,
            'last_query': history[-1][0].timestamp if history else None
        }