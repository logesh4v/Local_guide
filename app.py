"""
Streamlit application for Local Guide AI.
Provides a simple web interface for interacting with the local guide system.
"""
import streamlit as st
import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from local_guide_system import LocalGuideSystem


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'system' not in st.session_state:
        st.session_state.system = LocalGuideSystem()
        st.session_state.system.initialize()
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'selected_city' not in st.session_state:
        st.session_state.selected_city = None


def display_header():
    """Display the application header."""
    st.title("🏛️ Local Guide AI")
    st.markdown("*Your AI assistant for local guidance in Tamil Nadu cities*")
    
    # Display current city
    if st.session_state.selected_city:
        st.success(f"📍 Currently exploring: **{st.session_state.selected_city}**")
    else:
        st.info("👆 Please select a city to get started")


def display_city_selector():
    """Display city selection interface."""
    st.subheader("🌆 Select Your City")
    
    available_cities = st.session_state.system.get_available_cities()
    
    # City selection dropdown
    selected_city = st.selectbox(
        "Choose a city to explore:",
        options=[""] + available_cities,
        index=0 if not st.session_state.selected_city else available_cities.index(st.session_state.selected_city) + 1,
        key="city_selector"
    )
    
    # Handle city selection
    if selected_city and selected_city != st.session_state.selected_city:
        with st.spinner(f"Loading context for {selected_city}..."):
            success, message = st.session_state.system.select_city(selected_city)
            
            if success:
                st.session_state.selected_city = selected_city
                st.session_state.conversation_history = []  # Clear history on city change
                st.success(message)
                st.rerun()
            else:
                st.error(message)


def display_query_interface():
    """Display query input interface."""
    if not st.session_state.selected_city:
        st.warning("Please select a city first to ask questions.")
        return
    
    st.subheader("💬 Ask Your Question")
    
    # Use a form to handle query submission
    with st.form("query_form", clear_on_submit=True):
        query = st.text_input(
            "What would you like to know?",
            placeholder="e.g., Where can I find good biryani? How do I get to the temple?",
        )
        
        # Submit button
        submit_button = st.form_submit_button("Ask", type="primary", use_container_width=True)
        
        # Process query
        if submit_button and query.strip():
            with st.spinner("Thinking..."):
                response = st.session_state.system.process_query(query)
                
                # Add to conversation history
                st.session_state.conversation_history.append({
                    'query': query,
                    'response': response,
                    'timestamp': datetime.now()
                })
                
                # Rerun to refresh the interface
                st.rerun()
        
        elif submit_button and not query.strip():
            st.warning("Please enter a question.")


def display_response(response_data):
    """
    Display a response with appropriate styling.
    
    Args:
        response_data: Dictionary with response information
    """
    response = response_data['response']
    
    if response.is_refusal:
        # Display refusal with warning styling
        st.warning(f"🚫 **Sorry!** {response.text}")
        
        # Show refusal reason if available
        if response.refusal_reason and response.refusal_reason != "Information not available in context":
            with st.expander("Why can't I answer this?"):
                st.write(f"**Reason:** {response.refusal_reason}")
                st.write("**Supported topics:** food, transport, slang, safety, lifestyle")
    else:
        # Display successful response
        st.success(f"✅ {response.text}")


def display_conversation_history():
    """Display conversation history."""
    if not st.session_state.conversation_history:
        return
    
    st.subheader("💭 Conversation History")
    
    # Display conversations in reverse order (newest first)
    for i, conv in enumerate(reversed(st.session_state.conversation_history)):
        with st.expander(f"Q: {conv['query'][:50]}{'...' if len(conv['query']) > 50 else ''}", expanded=(i == 0)):
            st.write(f"**You asked:** {conv['query']}")
            st.write(f"**Response:**")
            display_response(conv)
            st.caption(f"Asked at {conv['timestamp'].strftime('%H:%M:%S')}")


def display_sidebar():
    """Display sidebar with system information and controls."""
    with st.sidebar:
        st.header("🔧 System Info")
        
        # System status
        status = st.session_state.system.get_system_status()
        
        if status['initialized']:
            st.success("✅ System Ready")
        else:
            st.error("❌ System Not Ready")
        
        # Current session info
        st.subheader("📊 Session Info")
        if status['selected_city']:
            st.write(f"**City:** {status['selected_city']}")
            st.write(f"**Conversations:** {status['conversation_length']}")
        else:
            st.write("No city selected")
        
        # Model information
        st.subheader("🤖 AI Model")
        model_info = status['model_info']
        st.write(f"**Model:** {model_info['model_id']}")
        st.write(f"**Provider:** {model_info['provider']}")
        st.write(f"**Temperature:** {model_info['temperature']}")
        
        # Usage statistics
        if st.session_state.conversation_history:
            stats = st.session_state.system.get_usage_statistics()
            st.subheader("📈 Usage Stats")
            st.write(f"**Total Queries:** {stats['total_queries']}")
            st.write(f"**Successful:** {stats['successful_responses']}")
            st.write(f"**Refusals:** {stats['refusal_responses']}")
            st.write(f"**Refusal Rate:** {stats['refusal_rate']:.1%}")
        
        # Controls
        st.subheader("🎛️ Controls")
        
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.system.reset_session()
            st.session_state.selected_city = None
            st.session_state.conversation_history = []
            st.success("Session reset!")
            st.rerun()
        
        if st.button("🏥 Health Check", use_container_width=True):
            health = st.session_state.system.validate_system_health()
            
            if health['overall_status'] == 'healthy':
                st.success("✅ All systems healthy")
            elif health['overall_status'] == 'warning':
                st.warning("⚠️ Some warnings detected")
            else:
                st.error("❌ System issues detected")
            
            if health['issues']:
                with st.expander("Issues Details"):
                    for issue in health['issues']:
                        st.write(f"• {issue}")


def display_help():
    """Display help information."""
    with st.expander("ℹ️ How to use this app"):
        st.markdown("""
        **Getting Started:**
        1. Select a city from the dropdown (Madurai or Dindigul)
        2. Ask questions about local topics
        
        **Supported Topics:**
        - 🍽️ **Food:** Restaurants, local dishes, specialties
        - 🚌 **Transport:** Buses, auto rickshaws, routes
        - 🗣️ **Language:** Local phrases, Tamil expressions
        - 🛡️ **Safety:** Safe areas, precautions, emergency contacts
        - 🎭 **Lifestyle:** Culture, festivals, shopping, customs
        
        **Example Questions:**
        - "Where can I find good biryani?"
        - "How do I get to the temple?"
        - "What does 'enna da' mean?"
        - "Is this area safe at night?"
        - "What festivals are celebrated here?"
        
        **Important Notes:**
        - I only provide information from local context files
        - If I don't know something, I'll tell you honestly
        - I focus on practical, local guidance
        """)


def main():
    """Main application function."""
    # Configure page
    st.set_page_config(
        page_title="Local Guide AI",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Main content
    display_header()
    display_help()
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_city_selector()
        display_query_interface()
        
        # Display latest response if available
        if st.session_state.conversation_history:
            st.subheader("💬 Latest Response")
            latest = st.session_state.conversation_history[-1]
            st.write(f"**You asked:** {latest['query']}")
            display_response(latest)
    
    with col2:
        display_conversation_history()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "🏛️ **Local Guide AI** - Built for Kiro Heroes Challenge Week 5 | "
        "Powered by Amazon Nova Premier via Bedrock"
    )


if __name__ == "__main__":
    main()