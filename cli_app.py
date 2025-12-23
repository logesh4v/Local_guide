"""
Command Line Interface for Local Guide AI.
Provides a terminal-based interface for interacting with the local guide system.
"""
import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from local_guide_system import LocalGuideSystem


class LocalGuideCLI:
    """Command Line Interface for Local Guide AI."""
    
    def __init__(self):
        """Initialize the CLI application."""
        self.system = LocalGuideSystem()
        self.current_city = None
        self.conversation_history = []
    
    def print_header(self):
        """Print application header."""
        print("=" * 60)
        print("🏛️  LOCAL GUIDE AI - Tamil Nadu Cities")
        print("=" * 60)
        print("Your AI assistant for local guidance in Madurai and Dindigul")
        print("Powered by Amazon Nova Premier via Bedrock")
        print("=" * 60)
    
    def print_separator(self):
        """Print a separator line."""
        print("-" * 60)
    
    def display_city_selection(self):
        """Display city selection menu."""
        print("\n🌆 CITY SELECTION")
        self.print_separator()
        
        available_cities = self.system.get_available_cities()
        
        print("Available cities:")
        for i, city in enumerate(available_cities, 1):
            print(f"  {i}. {city}")
        
        print("  0. Exit")
        
        while True:
            try:
                choice = input("\nSelect a city (enter number): ").strip()
                
                if choice == "0":
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_cities):
                    selected_city = available_cities[choice_num - 1]
                    
                    print(f"\n🔄 Loading context for {selected_city}...")
                    success, message = self.system.select_city(selected_city)
                    
                    if success:
                        self.current_city = selected_city
                        print(f"✅ {message}")
                        return selected_city
                    else:
                        print(f"❌ {message}")
                        continue
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return None
    
    def display_help(self):
        """Display help information."""
        print("\n📖 HELP & USAGE")
        self.print_separator()
        print("SUPPORTED TOPICS:")
        print("  🍽️  Food      - Restaurants, local dishes, specialties")
        print("  🚌 Transport - Buses, auto rickshaws, routes")
        print("  🗣️  Language  - Local phrases, Tamil expressions")
        print("  🛡️  Safety    - Safe areas, precautions, emergency contacts")
        print("  🎭 Lifestyle - Culture, festivals, shopping, customs")
        print()
        print("EXAMPLE QUESTIONS:")
        print("  • Where can I find good biryani?")
        print("  • How do I get to the temple?")
        print("  • What does 'enna da' mean?")
        print("  • Is this area safe at night?")
        print("  • What festivals are celebrated here?")
        print()
        print("COMMANDS:")
        print("  help    - Show this help")
        print("  status  - Show system status")
        print("  history - Show conversation history")
        print("  switch  - Switch to different city")
        print("  clear   - Clear conversation history")
        print("  exit    - Exit the application")
    
    def display_status(self):
        """Display system status."""
        print("\n📊 SYSTEM STATUS")
        self.print_separator()
        
        status = self.system.get_system_status()
        
        print(f"System Initialized: {'✅ Yes' if status['initialized'] else '❌ No'}")
        print(f"Selected City: {status['selected_city'] or 'None'}")
        print(f"Context Loaded: {'✅ Yes' if status['context_loaded'] else '❌ No'}")
        print(f"Conversations: {len(self.conversation_history)}")
        
        print(f"\nModel Information:")
        model_info = status['model_info']
        print(f"  Model: {model_info['model_id']}")
        print(f"  Provider: {model_info['provider']}")
        print(f"  Temperature: {model_info['temperature']}")
        
        if self.conversation_history:
            stats = self.system.get_usage_statistics()
            print(f"\nUsage Statistics:")
            print(f"  Total Queries: {stats['total_queries']}")
            print(f"  Successful: {stats['successful_responses']}")
            print(f"  Refusals: {stats['refusal_responses']}")
            print(f"  Refusal Rate: {stats['refusal_rate']:.1%}")
    
    def display_history(self):
        """Display conversation history."""
        if not self.conversation_history:
            print("\n📝 No conversation history yet.")
            return
        
        print(f"\n📝 CONVERSATION HISTORY ({len(self.conversation_history)} items)")
        self.print_separator()
        
        for i, (query, response, timestamp) in enumerate(self.conversation_history, 1):
            print(f"\n{i}. [{timestamp.strftime('%H:%M:%S')}]")
            print(f"   Q: {query}")
            
            if response.is_refusal:
                print(f"   A: 🚫 {response.text}")
            else:
                print(f"   A: ✅ {response.text}")
    
    def format_response(self, response):
        """
        Format response for CLI display.
        
        Args:
            response: Response object
            
        Returns:
            Formatted response string
        """
        if response.is_refusal:
            return f"🚫 Sorry! {response.text}"
        else:
            return f"✅ {response.text}"
    
    def process_command(self, user_input):
        """
        Process special commands.
        
        Args:
            user_input: User input string
            
        Returns:
            True if command was processed, False if it's a regular query
        """
        command = user_input.lower().strip()
        
        if command == "help":
            self.display_help()
            return True
        
        elif command == "status":
            self.display_status()
            return True
        
        elif command == "history":
            self.display_history()
            return True
        
        elif command == "switch":
            print("\n🔄 Switching city...")
            new_city = self.display_city_selection()
            if new_city:
                self.conversation_history.clear()
                print(f"✅ Switched to {new_city}. Conversation history cleared.")
            return True
        
        elif command == "clear":
            self.conversation_history.clear()
            print("✅ Conversation history cleared.")
            return True
        
        elif command in ["exit", "quit", "bye"]:
            return "exit"
        
        return False
    
    def main_loop(self):
        """Main interaction loop."""
        print(f"\n💬 CHAT WITH LOCAL GUIDE - {self.current_city}")
        self.print_separator()
        print("Ask me anything about local food, transport, language, safety, or lifestyle!")
        print("Type 'help' for more information or 'exit' to quit.")
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n[{self.current_city}] You: ").strip()
                
                if not user_input:
                    continue
                
                # Process commands
                command_result = self.process_command(user_input)
                if command_result == "exit":
                    break
                elif command_result:
                    continue
                
                # Process as query
                print("🤔 Thinking...")
                response = self.system.process_query(user_input)
                
                # Display response
                formatted_response = self.format_response(response)
                print(f"\nGuide: {formatted_response}")
                
                # Add to history
                self.conversation_history.append((user_input, response, datetime.now()))
                
                # Show additional info for refusals
                if response.is_refusal and response.refusal_reason:
                    if response.refusal_reason != "Information not available in context":
                        print(f"💡 Tip: {response.refusal_reason}")
                        print("💡 I can help with: food, transport, language, safety, lifestyle")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again or type 'exit' to quit.")
    
    def run(self):
        """Run the CLI application."""
        try:
            # Print header
            self.print_header()
            
            # Initialize system
            print("\n🔄 Initializing system...")
            if not self.system.initialize():
                print("❌ Failed to initialize system. Exiting.")
                return
            
            print("✅ System initialized successfully!")
            
            # City selection
            selected_city = self.display_city_selection()
            if not selected_city:
                print("\n👋 Goodbye!")
                return
            
            # Main interaction loop
            self.main_loop()
            
        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            print("Application will exit.")
        
        finally:
            print("\n👋 Thank you for using Local Guide AI!")


def main():
    """Main entry point for CLI application."""
    cli = LocalGuideCLI()
    cli.run()


if __name__ == "__main__":
    main()