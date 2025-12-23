# 🏛️ Local Guide AI

**Production-grade AI assistant for Tamil Nadu cities - Built for Kiro Heroes Challenge Week 5**

A context-driven AI application that provides locality-aware guidance for Madurai and Dindigul using Amazon Nova Premier via Bedrock, with strict hallucination prevention and controlled AI behavior.

## 📋 Table of Contents

- [🎯 What This App Does](#-what-this-app-does)
- [🏗️ Complete System Architecture](#️-complete-system-architecture)
- [📊 Detailed Data Flow](#-detailed-data-flow)
- [🚀 Complete Setup & Installation](#-complete-setup--installation)
- [💻 How to Run the Application](#-how-to-run-the-application)
- [💬 Comprehensive Usage Examples](#-comprehensive-usage-examples)
- [🔧 Advanced Configuration](#-advanced-configuration)
- [🧪 Testing & Validation](#-testing--validation)
- [📁 Project Structure](#-project-structure)
- [🛠️ Technology Stack](#️-technology-stack)
- [🚨 Troubleshooting Guide](#-troubleshooting-guide)
- [📈 Performance & Monitoring](#-performance--monitoring)

## 🎯 What This App Does

Local Guide AI is a specialized AI assistant that provides **accurate, context-driven guidance** for two Tamil Nadu cities: **Madurai** and **Dindigul**. Unlike general-purpose AI assistants, this system:

### Core Capabilities
- **🎯 Context-Only Responses**: Only uses authoritative local knowledge stored in markdown context files
- **🚫 Honest Refusal**: Refuses to answer when information isn't available rather than guessing or hallucinating
- **🏙️ City Isolation**: Maintains strict context isolation between cities - no mixing of information
- **🛡️ Hallucination Prevention**: Multi-layer validation prevents AI from generating false information
- **🗣️ Local Cultural Understanding**: Provides practical guidance with Tamil-English mix where appropriate
- **⚡ Real-time Processing**: Instant responses through optimized multi-agent pipeline

### Supported Topics
- **🍽️ Food & Dining**: Local specialties, restaurants, timing, cultural food practices
- **🚌 Transportation**: Buses, auto rickshaws, routes, pricing, safety tips
- **🗣️ Local Language**: Tamil phrases, slang, cultural expressions, communication tips
- **🛡️ Safety Information**: Area safety, precautions, emergency contacts, local customs
- **🎭 Lifestyle & Culture**: Festivals, shopping, customs, traditions, local practices

### What Makes It Different
- **No General Knowledge**: Won't answer questions about weather, news, or topics outside local context
- **Standardized Refusals**: Uses only 3 specific phrases when information isn't available
- **Context Supremacy**: Every response is traceable to authoritative local knowledge files
- **Multi-Agent Validation**: 4-layer processing ensures accuracy and prevents hallucinations

## 🏗️ Complete System Architecture

### Multi-Agent Architecture Overview

The system employs a **four-agent architecture** using the Strands Agents framework with Amazon Nova Premier:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────┐
│   User Input    │───▶│ Context Loader   │───▶│ Query Validator │───▶│ Local Guide  │
│  (Streamlit/CLI)│    │     Agent        │    │     Agent       │    │    Agent     │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └──────────────┘
                                │                        │                       │
                                ▼                        ▼                       ▼
                       ┌──────────────────┐    ┌─────────────────┐    ┌──────────────┐
                       │ Context Files    │    │ Supported Topics│    │ Nova Premier │
                       │ - madurai.md     │    │ - Food          │    │ via Bedrock  │
                       │ - dindigul.md    │    │ - Transport     │    │ (us-east-1)  │
                       └──────────────────┘    │ - Language      │    └──────────────┘
                                              │ - Safety        │            │
                                              │ - Lifestyle     │            ▼
                                              └─────────────────┘    ┌──────────────┐
                                                       │             │ Guard Agent  │
                                                       ▼             │ Validation   │
                                              ┌─────────────────┐    └──────────────┘
                                              │ Final Response  │            │
                                              │ or Refusal      │◀───────────┘
                                              └─────────────────┘
```

### Agent Responsibilities

#### 1. Context Loader Agent
- **Purpose**: Manages city-specific context file loading and isolation
- **Key Functions**:
  - `load_city_context(city: str)` - Loads markdown context for selected city
  - `get_available_cities()` - Returns supported cities (Madurai, Dindigul)
  - `validate_city_selection(city: str)` - Ensures valid city selection
- **Context Isolation**: Prevents mixing of information between cities
- **File Management**: Handles context file reading, validation, and caching

#### 2. Query Validation Agent  
- **Purpose**: Validates user queries for scope and appropriateness
- **Key Functions**:
  - `validate_query_scope(query: str)` - Checks if query is within supported topics
  - `is_supported_topic(query: str)` - Identifies topic category
  - `get_rejection_reason(query: str)` - Provides specific rejection reasoning
- **Supported Topics**: Food, transport, language, safety, lifestyle
- **Rejection Handling**: Provides clear feedback for out-of-scope queries

#### 3. Local Guide Agent
- **Purpose**: Primary response generation using Amazon Nova Premier
- **Key Functions**:
  - `generate_response(query: str, context: str)` - Creates contextual responses
  - `configure_model()` - Sets up Bedrock connection and model parameters
  - `apply_system_prompt(context: str)` - Enforces context-only behavior
- **Model Configuration**: Nova Premier with temperature=0.1, max_tokens=2048
- **System Prompt**: Enforces context supremacy and refusal behavior

#### 4. Guard Agent
- **Purpose**: Post-processing validation to prevent hallucinations
- **Key Functions**:
  - `validate_response(response: str, context: str)` - Ensures context adherence
  - `detect_hallucination(response: str, context: str)` - Identifies external knowledge
  - `force_refusal(reason: str)` - Generates standardized refusal responses
- **Validation Rules**: No external knowledge, no speculation, context-only information
- **Refusal Enforcement**: Uses only approved refusal phrases

## � Doetailed Data Flow

### Complete Request Processing Pipeline

```
1. USER INPUT
   ├─ Streamlit Interface: City selection dropdown + text input
   ├─ CLI Interface: Interactive prompts and text input
   └─ Input validation: Non-empty, reasonable length

2. CONTEXT LOADING
   ├─ Context Loader Agent receives city selection
   ├─ Loads corresponding markdown file:
   │  ├─ context/madurai_context.md (for Madurai)
   │  └─ context/dindigul_context.md (for Dindigul)
   ├─ Validates file integrity and content
   └─ Stores context in system memory (isolated per city)

3. QUERY VALIDATION
   ├─ Query Validator Agent receives user query
   ├─ Checks against supported topics:
   │  ├─ Food & dining keywords
   │  ├─ Transportation keywords  
   │  ├─ Language & slang keywords
   │  ├─ Safety & security keywords
   │  └─ Lifestyle & culture keywords
   ├─ Validates query appropriateness
   └─ Decision: ACCEPT (continue) or REJECT (return refusal)

4. RESPONSE GENERATION
   ├─ Local Guide Agent receives validated query + context
   ├─ Constructs system prompt with context supremacy rules
   ├─ Sends to Amazon Nova Premier via Bedrock:
   │  ├─ Model: us.amazon.nova-premier-v1:0
   │  ├─ Temperature: 0.1 (low for consistency)
   │  ├─ Max tokens: 2048
   │  └─ Region: us-east-1
   ├─ Receives model response
   └─ Applies local tone and Tamil-English mix

5. GUARD VALIDATION
   ├─ Guard Agent receives generated response + original context
   ├─ Validates response against context:
   │  ├─ Checks for external knowledge
   │  ├─ Verifies information accuracy
   │  ├─ Ensures no hallucinations
   │  └─ Confirms context adherence
   ├─ Decision: APPROVE (return response) or REJECT (force refusal)
   └─ Applies standardized refusal if needed

6. RESPONSE DELIVERY
   ├─ Format response for interface (Streamlit/CLI)
   ├─ Add conversation to history
   ├─ Update usage statistics
   └─ Display to user with appropriate styling
```

### Context Supremacy Enforcement

**System Prompt Structure**:
```
You are a local guide for [CITY_NAME] only. 

STRICT RULES:
1. Only use information from the provided context
2. If information is not in context, use ONLY these refusal phrases:
   - "This isn't covered in my local context."
   - "I don't have enough local data to answer that."  
   - "My knowledge is limited to what's in the context file."
3. Never use general world knowledge
4. Never speculate or infer beyond the context
5. Maintain local tone with Tamil-English mix where appropriate

CONTEXT FOR [CITY_NAME]:
[LOADED_CONTEXT_CONTENT]
```

### Error Handling Flow

```
ERROR SCENARIOS:
├─ Context Loading Errors
│  ├─ File not found → Clear error message + prevent city selection
│  ├─ Malformed content → Log error + user-friendly message
│  └─ Permission issues → Error message + fallback behavior
├─ Query Processing Errors  
│  ├─ Empty queries → Rejection with feedback
│  ├─ Extremely long queries → Truncation or rejection
│  └─ Special characters → Graceful handling
├─ Model Integration Errors
│  ├─ Bedrock unavailable → Clear error + retry suggestion
│  ├─ Authentication failure → Credential configuration guidance
│  ├─ Rate limiting → Backoff strategy + user notification
│  └─ Model unavailable → Graceful error handling
└─ Guard Validation Errors
   ├─ Validation failure → Default to refusal for safety
   └─ Processing errors → Log issue + force refusal
```

## 🚀 Complete Setup & Installation

### Prerequisites & Requirements

**System Requirements:**
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.10 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 500MB free space
- **Network**: Internet connection for AWS Bedrock API calls

**AWS Requirements:**
- **AWS Account** with active subscription
- **Amazon Bedrock** service access enabled
- **Nova Premier Model** access granted (requires model access request)
- **IAM Permissions** for Bedrock API calls

### Step-by-Step Installation

#### Step 1: Clone the Repository
```bash
# Clone from GitHub
git clone https://github.com/logesh4v/Local_guide.git

# Navigate to project directory
cd Local_guide
```

#### Step 2: Python Environment Setup
```bash
# Check Python version (must be 3.10+)
python --version

# Create virtual environment (recommended)
python -m venv local-guide-env

# Activate virtual environment
# On Windows:
local-guide-env\Scripts\activate
# On macOS/Linux:
source local-guide-env/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(strands|streamlit|boto3|hypothesis)"
```

**Key Dependencies Installed:**
- `strands-agents>=0.1.0` - Multi-agent framework
- `strands-agents-tools>=0.1.0` - Agent tools and utilities
- `streamlit>=1.28.0` - Web interface framework
- `boto3>=1.34.0` - AWS SDK for Python
- `hypothesis>=6.88.0` - Property-based testing
- `pytest>=7.4.0` - Testing framework
- `python-dotenv>=1.0.0` - Environment variable management

#### Step 4: AWS Configuration

**Option 1: Bedrock API Key (Recommended for Development)**
```bash
# Set environment variable (replace with your actual key)
export AWS_BEARER_TOKEN_BEDROCK=your_bedrock_bearer_token_here

# On Windows Command Prompt:
set AWS_BEARER_TOKEN_BEDROCK=your_bedrock_bearer_token_here

# On Windows PowerShell:
$env:AWS_BEARER_TOKEN_BEDROCK="your_bedrock_bearer_token_here"
```

**Option 2: Standard AWS Credentials**
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_REGION=us-east-1

# Or use AWS CLI configuration
aws configure
```

**Option 3: Environment File (Secure)**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your credentials
# AWS_BEARER_TOKEN_BEDROCK=your_token_here
# AWS_REGION=us-east-1
```

#### Step 5: Enable Nova Premier Model Access

1. **Login to AWS Console**: https://console.aws.amazon.com/bedrock
2. **Navigate to Model Access**: 
   - Go to "Bedrock" service
   - Click "Model access" in left sidebar
   - Click "Manage model access"
3. **Enable Nova Premier**:
   - Find "Amazon Nova Premier" in the list
   - Check the box to enable access
   - Click "Request model access" if needed
   - Wait for approval (usually instant for existing accounts)
4. **Verify Access**:
   - Ensure status shows "Access granted"
   - Note the model ID: `us.amazon.nova-premier-v1:0`

#### Step 6: Verify Installation
```bash
# Test basic imports
python test_import.py

# Run quick validation
python quick_validation.py

# Check system health
python -c "from local_guide_system import LocalGuideSystem; system = LocalGuideSystem(); system.initialize(); print('✅ Installation successful!')"
```

### Configuration Files Overview

**`.env.example`** - Template for environment variables
```bash
# AWS Configuration for Local Guide AI
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_bearer_token_here
AWS_ACCESS_KEY_ID=your_access_key_here  
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

**`.kiro/system_prompt.txt`** - AI behavior configuration
- Enforces context supremacy rules
- Defines refusal response formats
- Sets local tone guidelines

**`context/madurai_context.md`** - Madurai knowledge base
**`context/dindigul_context.md`** - Dindigul knowledge base

## 💻 How to Run the Application

### Method 1: Streamlit Web Interface (Recommended)

**Start the Web Application:**
```bash
# Navigate to project directory
cd Local_guide

# Start Streamlit server
streamlit run app.py

# Application will open at: http://localhost:8501
```

**Web Interface Features:**
- **City Selection Dropdown**: Choose between Madurai and Dindigul
- **Query Input Form**: Type questions with auto-clear after submission
- **Response Display**: Formatted responses with refusal highlighting
- **Conversation History**: Track all interactions in current session
- **System Status Sidebar**: Monitor system health and statistics
- **Usage Analytics**: View query counts, success rates, and refusal rates

**Web Interface Workflow:**
1. **Select City**: Choose Madurai or Dindigul from dropdown
2. **Wait for Context Loading**: System loads city-specific knowledge
3. **Ask Questions**: Type queries in the input field
4. **Review Responses**: See formatted answers or refusal messages
5. **Check History**: Review previous questions and answers
6. **Monitor Stats**: View usage statistics in sidebar

### Method 2: Command Line Interface (CLI)

**Start the CLI Application:**
```bash
# Navigate to project directory
cd Local_guide

# Start CLI interface
python cli_app.py
```

**CLI Interface Features:**
- **Interactive City Selection**: Numbered menu for city choice
- **Clean Text Input**: Simple prompt-based question entry
- **Formatted Output**: Clear response display with refusal highlighting
- **Session Management**: Track conversation within CLI session
- **Status Commands**: Check system health and statistics

**CLI Commands:**
```bash
# Basic usage
python cli_app.py

# Available CLI commands during session:
# 'status' - Check system health
# 'stats' - View usage statistics  
# 'switch' - Change city selection
# 'history' - View conversation history
# 'help' - Show available commands
# 'quit' or 'exit' - End session
```

### Method 3: Automated Setup Script

**Quick Start with Setup Script:**
```bash
# Run automated setup and launch
python setup_and_run.py

# This script will:
# 1. Check AWS credentials
# 2. Validate system requirements
# 3. Test model connectivity
# 4. Launch Streamlit interface
```

### Method 4: Development Mode

**For Development and Testing:**
```bash
# Run comprehensive test suite
python comprehensive_test.py

# Run specific test categories
pytest testing/test_*_unit.py          # Unit tests
pytest testing/test_*_property.py      # Property-based tests
pytest testing/test_integration.py     # Integration tests

# Quick system validation
python quick_validation.py

# Test specific components
python test_query_validation.py
python test_rag.py
```

## 💬 Comprehensive Usage Examples

### ✅ Supported Queries (Will Get Helpful Responses)

#### 🍽️ Food & Dining Queries

**General Food Questions:**
- **Query**: "What food is Madurai famous for?"
- **Expected Response**: Information about Madurai's food specialties, local dishes, and cultural significance

**Specific Restaurant Recommendations:**
- **Query**: "Where can I find good biryani in Dindigul?"
- **Expected Response**: Specific restaurant names, locations, and timing information from context

**Local Specialties:**
- **Query**: "What is Jigarthanda? Where can I get it?"
- **Expected Response**: Description of the drink and places to find it in Madurai

**Time-Sensitive Food Queries:**
- **Query**: "Can I get fresh biryani at 8 AM in Dindigul?"
- **Expected Response**: Information about morning availability and freshness

**Cultural Food Practices:**
- **Query**: "What do locals eat for breakfast in Madurai?"
- **Expected Response**: Traditional breakfast items and local preferences

#### 🚌 Transportation Queries

**Auto Rickshaw Information:**
- **Query**: "Are auto rickshaws cheap in Dindigul?"
- **Expected Response**: Pricing information, meter usage, and negotiation tips

**Bus Routes and Services:**
- **Query**: "How do I get to Meenakshi Temple by bus?"
- **Expected Response**: Bus route numbers, stops, and timing information

**Local Transport Tips:**
- **Query**: "What's the best way to travel around Madurai?"
- **Expected Response**: Comparison of transport options with local insights

**Safety and Pricing:**
- **Query**: "Do autos use meters in Madurai?"
- **Expected Response**: Information about meter usage and fare practices

#### 🗣️ Local Language & Slang

**Common Phrases:**
- **Query**: "What does 'enna da' mean?"
- **Expected Response**: Translation, context, and usage examples

**Cultural Expressions:**
- **Query**: "How do people greet each other in Madurai?"
- **Expected Response**: Local greeting customs and phrases

**Slang and Colloquialisms:**
- **Query**: "What does 'Sema da' mean?"
- **Expected Response**: Explanation of the expression and when it's used

**Communication Tips:**
- **Query**: "Teach me some basic Tamil phrases for shopping"
- **Expected Response**: Useful phrases with pronunciation guidance

#### 🛡️ Safety & Security

**Area Safety:**
- **Query**: "Is Dindigul safe at night?"
- **Expected Response**: Safety information, precautions, and local insights

**General Precautions:**
- **Query**: "What safety precautions should I take in Madurai?"
- **Expected Response**: Specific safety tips and local advice

**Emergency Information:**
- **Query**: "What are the emergency contact numbers?"
- **Expected Response**: Local emergency contacts and procedures

#### 🎭 Lifestyle & Culture

**Festivals and Events:**
- **Query**: "What festivals are celebrated in Madurai?"
- **Expected Response**: Local festivals, timing, and cultural significance

**Shopping and Markets:**
- **Query**: "Where can I shop for traditional items in Dindigul?"
- **Expected Response**: Market locations, items available, and shopping tips

**Local Customs:**
- **Query**: "Tell me about local customs I should know"
- **Expected Response**: Cultural practices and etiquette guidelines

### 🚫 Expected Refusals (Honest "I Don't Know" Responses)

The system will refuse to answer queries outside its scope using exactly one of these three phrases:

#### Out-of-Scope Topics

**General World Knowledge:**
- **Query**: "What's the weather like in New York?"
- **Refusal**: *"My knowledge is limited to what's in the context file."*

**Current Events/News:**
- **Query**: "What's the latest political news in Tamil Nadu?"
- **Refusal**: *"This isn't covered in my local context."*

**Medical/Legal Advice:**
- **Query**: "Can you diagnose my medical condition?"
- **Refusal**: *"I don't have enough local data to answer that."*

**Technical Support:**
- **Query**: "Help me fix my computer"
- **Refusal**: *"This isn't covered in my local context."*

#### Information Not in Context Files

**Statistical Data:**
- **Query**: "What's the exact population of Madurai?"
- **Refusal**: *"I don't have enough local data to answer that."*

**Historical Details:**
- **Query**: "When exactly was Meenakshi Temple built?"
- **Refusal**: *"My knowledge is limited to what's in the context file."*

**Specific Business Hours:**
- **Query**: "What time does XYZ restaurant close on Sundays?"
- **Refusal**: *"This isn't covered in my local context."*

#### Other Cities/Locations

**Non-Supported Cities:**
- **Query**: "Tell me about restaurants in Chennai"
- **Refusal**: *"My knowledge is limited to what's in the context file."*

**International Queries:**
- **Query**: "How do I get from Madurai to Singapore?"
- **Refusal**: *"This isn't covered in my local context."*

### 📝 Sample Conversation Flow

**Complete Interaction Example:**

```
👤 User: [Selects Madurai from dropdown]
🤖 System: ✅ Context loaded for Madurai. Ready for your questions!

👤 User: "What should I try for breakfast in Madurai?"
🤖 System: "In Madurai, locals typically start their day with idli, dosa, or pongal. 
          You'll find excellent filter coffee at most places. Try the local 
          specialty 'kari dosa' if you want something unique to the region."

👤 User: "Where can I get good kari dosa?"
🤖 System: "You can find authentic kari dosa at several local eateries in 
          Madurai. The dish is particularly popular at traditional South 
          Indian restaurants in the city center."

👤 User: "What's the population of Madurai?"
🤖 System: 🚫 "I don't have enough local data to answer that."

👤 User: "How do I get to Meenakshi Temple?"
🤖 System: "The Meenakshi Temple is well-connected by local buses and auto 
          rickshaws. Most auto drivers know the temple location. You can 
          also take city buses that stop near the temple complex."
```

### 🎯 Query Optimization Tips

**For Best Results:**
- **Be Specific**: "Where can I find biryani in Dindigul?" vs "Tell me about food"
- **Use Local Context**: Ask about specific cities (Madurai/Dindigul)
- **Focus on Supported Topics**: Food, transport, language, safety, lifestyle
- **Ask Practical Questions**: "How do I..." vs "What is the history of..."

**Avoid These Query Types:**
- General world knowledge questions
- Current events or news
- Medical or legal advice
- Technical troubleshooting
- Information about other cities
- Statistical or historical data not in context

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Agent Framework:** Strands Agents SDK
- **LLM Provider:** Amazon Bedrock
- **Model:** Amazon Nova Premier (`us.amazon.nova-premier-v1:0`)
- **UI Framework:** Streamlit (Web) + CLI
- **Context Storage:** Markdown files
- **Testing:** Pytest + Hypothesis (Property-Based Testing)

## 🧪 Testing

The application includes comprehensive testing:

**Run all tests:**
```bash
pytest testing/
```

**Run specific test categories:**
```bash
# Property-based tests
pytest testing/test_*_property.py

# Unit tests  
pytest testing/test_*_unit.py

# Context isolation tests
pytest testing/test_context_isolation.py
```

## 📊 System Features

### Context-Driven AI Control
- Strict adherence to local knowledge files
- No general world knowledge allowed
- Honest refusal when information unavailable

### Local Cultural Understanding
- Tamil-English language mix
- Cultural context and customs
- Local terminology and phrases

### Responsible Refusal Behavior
- Three standardized refusal phrases
- Clear communication of limitations
- Helpful guidance on supported topics

### Clean Engineering Discipline
- Multi-agent architecture
- Comprehensive error handling
- Property-based testing
- Clear separation of concerns

## 🔧 Configuration

### System Prompt Configuration
Edit `.kiro/system_prompt.txt` to modify AI behavior:
- Context supremacy rules
- Refusal response formats
- Response style guidelines

### Context Files
Update context files to add local knowledge:
- `context/madurai_context.md` - Madurai-specific information
- `context/dindigul_context.md` - Dindigul-specific information

## 🚨 Troubleshooting

### Common Issues

**"Model connection test failed"**
- Ensure AWS credentials are configured
- Verify Nova Premier model access is enabled
- Check AWS region is set to `us-east-1`

**"Context file not found"**
- Ensure you're running from the `local-guide-kiro` directory
- Verify context files exist in the `context/` folder

**"Invalid city selection"**
- Only Madurai and Dindigul are supported
- Check spelling and capitalization

### Getting Help

1. **Check system status** in the app (Streamlit sidebar or CLI `status` command)
2. **Run health check** to identify component issues
3. **Review error messages** for specific guidance
4. **Verify AWS credentials** and model access

## 🎯 Design Principles

1. **Context Supremacy** - Only use information from context files
2. **Honest Refusal** - Prefer "I don't know" over guessing
3. **Local Focus** - Practical, grounded local guidance
4. **Cultural Sensitivity** - Respect local customs and language
5. **Engineering Excellence** - Clean, testable, maintainable code

## 📈 Usage Statistics

The application tracks:
- Total queries processed
- Successful vs. refusal responses
- Refusal rate and reasons
- Conversation history per session

## 🏆 Kiro Heroes Challenge

This application demonstrates:
- **Strong context steering** through documentation-driven AI behavior
- **Locality awareness** with city-specific knowledge isolation
- **Controlled AI behavior** with multi-layer validation and refusal mechanisms
- **Production-grade engineering** with comprehensive testing and error handling

Built with ❤️ for the Kiro Heroes Challenge Week 5: The Local Guide

## 🔧 Advanced Configuration

### System Prompt Customization

**Edit `.kiro/system_prompt.txt` to modify AI behavior:**

```
You are a local guide for {city_name} only. You provide practical, helpful guidance based solely on the context provided.

STRICT RULES:
1. Only use information from the provided context
2. If information is not in context, use ONLY these refusal phrases:
   - "This isn't covered in my local context."
   - "I don't have enough local data to answer that."
   - "My knowledge is limited to what's in the context file."
3. Never use general world knowledge
4. Never speculate or infer beyond the context
5. Maintain local tone with Tamil-English mix where appropriate
6. Be practical and helpful within context limitations

CONTEXT FOR {city_name}:
{context_content}
```

### Context File Management

**Adding New Information to Context Files:**

1. **Edit Context Files**: Update `context/madurai_context.md` or `context/dindigul_context.md`
2. **Follow Structure**: Maintain consistent formatting and sections
3. **Verify Information**: Ensure all information is accurate and authoritative
4. **Test Changes**: Run validation tests after updates

**Context File Structure:**
```markdown
# City Name Context

## Food & Dining
- Local specialties
- Restaurant recommendations
- Timing and availability
- Cultural food practices

## Transportation
- Auto rickshaw information
- Bus routes and services
- Pricing and safety tips

## Local Language & Slang
- Common phrases and meanings
- Cultural expressions
- Communication tips

## Safety & Security
- Area safety information
- General precautions
- Emergency contacts

## Lifestyle & Culture
- Festivals and events
- Shopping locations
- Local customs and etiquette
```

### Model Configuration

**Adjust Model Parameters in `agents/local_guide_agent.py`:**

```python
# Model configuration options
model_config = {
    "model_id": "us.amazon.nova-premier-v1:0",
    "region_name": "us-east-1", 
    "temperature": 0.1,  # Lower = more consistent, Higher = more creative
    "max_tokens": 2048,  # Maximum response length
}
```

**Temperature Settings:**
- **0.0-0.2**: Very consistent, factual responses (recommended)
- **0.3-0.5**: Slightly more varied responses
- **0.6-1.0**: More creative but less predictable (not recommended)

### Environment Variables

**Complete Environment Configuration:**

```bash
# AWS Bedrock Configuration
AWS_BEARER_TOKEN_BEDROCK=your_token_here
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Application Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
LOG_LEVEL=INFO

# Development Settings
DEBUG_MODE=false
ENABLE_DETAILED_LOGGING=false
```

## 🧪 Testing & Validation

### Comprehensive Testing Suite

**Run All Tests:**
```bash
# Complete test suite
pytest testing/ -v

# With coverage report
pytest testing/ --cov=. --cov-report=html

# Specific test categories
pytest testing/test_*_unit.py -v          # Unit tests
pytest testing/test_*_property.py -v      # Property-based tests  
pytest testing/test_integration.py -v     # Integration tests
pytest testing/test_*_interface.py -v     # UI tests
```

### Property-Based Testing

**The system uses Hypothesis for property-based testing:**

```python
# Example property test
@given(st.text(min_size=1, max_size=100))
def test_query_validation_property(query):
    """Property: All non-empty queries should be processed without errors"""
    validator = QueryValidationAgent()
    result = validator.validate_query_scope(query)
    assert isinstance(result, bool)
```

**Property Tests Validate:**
- **Context Isolation**: City contexts never mix
- **Query Validation**: Supported topics are correctly identified
- **Response Generation**: All responses come from context only
- **Refusal Consistency**: Standardized refusal phrases are used
- **Guard Validation**: External knowledge is detected and blocked

### Manual Testing Scenarios

**Test Context Isolation:**
1. Select Madurai, ask about Dindigul-specific information
2. Switch to Dindigul, verify Madurai context is cleared
3. Confirm no cross-contamination of city information

**Test Refusal Behavior:**
1. Ask out-of-scope questions (weather, news, medical advice)
2. Verify only approved refusal phrases are used
3. Confirm no hallucinated information is provided

**Test Supported Topics:**
1. Ask questions about each supported topic category
2. Verify responses contain only context-based information
3. Confirm local tone and Tamil-English mix where appropriate

### Performance Testing

**Load Testing:**
```bash
# Simulate multiple concurrent users
python testing/load_test.py --users=10 --duration=60

# Memory usage monitoring
python testing/memory_test.py

# Response time benchmarking
python testing/benchmark_test.py
```

## 📁 Project Structure

```
Local_guide/
├── 📁 agents/                    # Multi-agent architecture
│   ├── __init__.py              # Package initialization
│   ├── context_loader.py        # City context management
│   ├── query_validator.py       # Query scope validation
│   ├── local_guide_agent.py     # Nova Premier integration
│   └── guard_agent.py           # Response validation
├── 📁 context/                   # Knowledge base
│   ├── __init__.py              # Package initialization
│   ├── madurai_context.md       # Madurai local knowledge
│   └── dindigul_context.md      # Dindigul local knowledge
├── 📁 testing/                   # Comprehensive test suite
│   ├── __init__.py              # Package initialization
│   ├── test_*_unit.py           # Unit tests for agents
│   ├── test_*_property.py       # Property-based tests
│   ├── test_integration.py      # End-to-end tests
│   └── test_*_interface.py      # UI/CLI tests
├── 📁 docs/                      # Specification documents
│   ├── requirements.md          # EARS-compliant requirements
│   ├── design.md               # Architecture & design
│   └── tasks.md                # Implementation plan
├── 📁 .kiro/                     # Kiro configuration
│   └── system_prompt.txt        # AI behavior configuration
├── 📄 app.py                     # Streamlit web interface
├── 📄 cli_app.py                 # Command-line interface
├── 📄 local_guide_system.py      # Main orchestration system
├── 📄 models.py                  # Core data models
├── 📄 rag_retriever.py           # RAG context retrieval
├── 📄 refusal_handler.py         # Standardized refusals
├── 📄 comprehensive_test.py      # Complete test runner
├── 📄 quick_validation.py        # System health check
├── 📄 setup_and_run.py          # Automated setup script
├── 📄 requirements.txt           # Python dependencies
├── 📄 .env.example              # Environment template
├── 📄 .gitignore               # Git ignore rules
└── 📄 README.md                # This documentation
```

### Key File Descriptions

**Core Application Files:**
- **`local_guide_system.py`**: Central orchestration system coordinating all agents
- **`models.py`**: Data models (CityContext, Query, Response, AppState)
- **`app.py`**: Streamlit web interface with sidebar controls and session management
- **`cli_app.py`**: Command-line interface for terminal usage

**Agent Architecture:**
- **`agents/context_loader.py`**: Loads and manages city-specific context files
- **`agents/query_validator.py`**: Validates queries against supported topics
- **`agents/local_guide_agent.py`**: Main response generation using Nova Premier
- **`agents/guard_agent.py`**: Post-processing validation and hallucination prevention

**Supporting Systems:**
- **`rag_retriever.py`**: RAG-based context retrieval system for time-aware responses
- **`refusal_handler.py`**: Standardized refusal response management
- **`comprehensive_test.py`**: Complete test runner with question bank validation

## 🛠️ Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Language** | Python | 3.10+ | Core application development |
| **Agent Framework** | Strands Agents SDK | >=0.1.0 | Multi-agent architecture |
| **LLM Provider** | Amazon Bedrock | Latest | Cloud AI service platform |
| **AI Model** | Nova Premier | v1:0 | Primary language model |
| **Web Framework** | Streamlit | >=1.28.0 | User interface |
| **AWS SDK** | Boto3 | >=1.34.0 | AWS service integration |
| **Testing** | Pytest + Hypothesis | >=7.4.0 | Unit & property-based testing |
| **Environment** | Python-dotenv | >=1.0.0 | Configuration management |

### Architecture Patterns

**Multi-Agent Pattern:**
- **Separation of Concerns**: Each agent has a specific responsibility
- **Pipeline Processing**: Sequential agent processing with validation
- **Error Isolation**: Agent failures don't cascade to other components
- **Testability**: Individual agents can be tested in isolation

**Context-Driven Design:**
- **Single Source of Truth**: Context files are authoritative
- **Immutable Context**: Context doesn't change during processing
- **Context Isolation**: Strict separation between city contexts
- **Validation Layers**: Multiple validation points ensure context adherence

**Defensive Programming:**
- **Input Validation**: All inputs validated before processing
- **Error Handling**: Graceful degradation on failures
- **Logging**: Comprehensive logging for debugging
- **Health Checks**: System health monitoring and reporting

### AWS Integration

**Bedrock Configuration:**
- **Region**: us-east-1 (required for Nova Premier)
- **Model ID**: us.amazon.nova-premier-v1:0
- **Authentication**: Bearer token or IAM credentials
- **Rate Limiting**: Built-in retry logic with exponential backoff

**Security Considerations:**
- **Credential Management**: Environment variables for sensitive data
- **API Key Rotation**: Support for credential updates without restart
- **Network Security**: HTTPS-only communication with AWS
- **Access Control**: Minimal required permissions for Bedrock access

## 🚨 Troubleshooting Guide

### Common Issues & Solutions

#### AWS Connection Issues

**Problem**: "Model connection test failed"
```
❌ Error: Unable to connect to Amazon Bedrock
```

**Solutions:**
1. **Check AWS Credentials:**
   ```bash
   # Verify environment variables
   echo $AWS_BEARER_TOKEN_BEDROCK
   echo $AWS_ACCESS_KEY_ID
   echo $AWS_SECRET_ACCESS_KEY
   echo $AWS_REGION
   ```

2. **Verify Model Access:**
   - Login to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock)
   - Check "Model access" → Ensure Nova Premier is enabled
   - Verify region is set to us-east-1

3. **Test Connectivity:**
   ```bash
   # Test AWS connection
   python -c "import boto3; client = boto3.client('bedrock-runtime', region_name='us-east-1'); print('✅ Connection successful')"
   ```

#### Context Loading Issues

**Problem**: "Context file not found"
```
❌ Error: Could not load context for [city]
```

**Solutions:**
1. **Verify File Existence:**
   ```bash
   # Check context files
   ls -la context/
   # Should show: madurai_context.md, dindigul_context.md
   ```

2. **Check File Permissions:**
   ```bash
   # Ensure files are readable
   chmod 644 context/*.md
   ```

3. **Validate File Content:**
   ```bash
   # Check file is not empty
   wc -l context/madurai_context.md
   wc -l context/dindigul_context.md
   ```

#### Installation Issues

**Problem**: "Module not found" errors
```
❌ ImportError: No module named 'strands_agents'
```

**Solutions:**
1. **Reinstall Dependencies:**
   ```bash
   # Clean install
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

2. **Check Python Version:**
   ```bash
   # Ensure Python 3.10+
   python --version
   ```

3. **Virtual Environment:**
   ```bash
   # Create fresh environment
   python -m venv fresh-env
   source fresh-env/bin/activate  # Linux/Mac
   fresh-env\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

#### Streamlit Issues

**Problem**: Streamlit won't start or crashes
```
❌ Error: Address already in use
```

**Solutions:**
1. **Change Port:**
   ```bash
   # Use different port
   streamlit run app.py --server.port 8502
   ```

2. **Kill Existing Process:**
   ```bash
   # Find and kill Streamlit processes
   pkill -f streamlit
   # Or on Windows:
   taskkill /f /im python.exe
   ```

3. **Clear Streamlit Cache:**
   ```bash
   # Clear cache directory
   rm -rf ~/.streamlit/
   ```

### System Health Checks

**Automated Health Check:**
```bash
# Run comprehensive health check
python quick_validation.py

# Expected output:
# ✅ Python version: 3.10+
# ✅ Dependencies installed
# ✅ AWS credentials configured
# ✅ Context files present
# ✅ Model connectivity
# ✅ System ready
```

**Manual Health Verification:**
```bash
# Test each component individually
python -c "from agents.context_loader import ContextLoaderAgent; print('✅ Context Loader OK')"
python -c "from agents.query_validator import QueryValidationAgent; print('✅ Query Validator OK')"
python -c "from agents.local_guide_agent import LocalGuideAgent; print('✅ Local Guide OK')"
python -c "from agents.guard_agent import GuardAgent; print('✅ Guard Agent OK')"
```

### Performance Issues

**Problem**: Slow response times
```
⚠️ Warning: Response taking longer than expected
```

**Solutions:**
1. **Check Network Connectivity:**
   ```bash
   # Test AWS endpoint connectivity
   ping bedrock-runtime.us-east-1.amazonaws.com
   ```

2. **Monitor Resource Usage:**
   ```bash
   # Check system resources
   python testing/memory_test.py
   ```

3. **Optimize Model Parameters:**
   - Reduce max_tokens if responses are too long
   - Check temperature setting (should be 0.1)
   - Verify region is us-east-1 (closest to Nova Premier)

### Debug Mode

**Enable Detailed Logging:**
```bash
# Set debug environment
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG

# Run with verbose output
python app.py --debug
```

**Log File Locations:**
- **Application Logs**: `logs/application.log`
- **Error Logs**: `logs/errors.log`
- **Agent Logs**: `logs/agents/`

### Getting Help

**If Issues Persist:**

1. **Check System Status:**
   - Run health check: `python quick_validation.py`
   - Review error logs in `logs/` directory
   - Test individual components

2. **Gather Debug Information:**
   ```bash
   # Collect system information
   python --version
   pip list | grep -E "(strands|streamlit|boto3)"
   echo $AWS_REGION
   ls -la context/
   ```

3. **Test Minimal Configuration:**
   - Use CLI interface instead of Streamlit
   - Test with simple queries
   - Verify AWS credentials separately

4. **Community Resources:**
   - Check project documentation in `docs/` folder
   - Review test cases in `testing/` directory
   - Examine configuration examples in `.env.example`

## 📈 Performance & Monitoring

### Usage Statistics

**The application tracks comprehensive metrics:**

**Query Metrics:**
- Total queries processed
- Successful responses vs. refusals
- Response time distribution
- Error rates by category

**Context Metrics:**
- Context loading times
- Context switching frequency
- Context validation success rates

**Agent Performance:**
- Individual agent processing times
- Agent error rates
- Pipeline throughput

**User Behavior:**
- Most common query types
- City selection preferences
- Session duration and interaction patterns

### Monitoring Dashboard

**Streamlit Sidebar Statistics:**
```
📊 Session Info
City: Madurai
Conversations: 15

🤖 AI Model  
Model: us.amazon.nova-premier-v1:0
Provider: Amazon Bedrock
Temperature: 0.1

📈 Usage Stats
Total Queries: 15
Successful: 12
Refusals: 3
Refusal Rate: 20.0%
```

### Performance Optimization

**Response Time Optimization:**
- **Context Caching**: Loaded contexts are cached in memory
- **Connection Pooling**: Reuse AWS connections when possible
- **Async Processing**: Non-blocking operations where applicable
- **Smart Validation**: Early rejection of invalid queries

**Memory Management:**
- **Context Cleanup**: Automatic cleanup of unused contexts
- **Session Management**: Efficient session state handling
- **Garbage Collection**: Proactive memory cleanup

**Network Optimization:**
- **Regional Deployment**: Use us-east-1 for Nova Premier
- **Retry Logic**: Exponential backoff for failed requests
- **Timeout Management**: Appropriate timeouts for different operations

---

## 🏆 Kiro Heroes Challenge

This application demonstrates:

- **🎯 Strong Context Steering**: Documentation-driven AI behavior with strict context supremacy
- **🏙️ Locality Awareness**: City-specific knowledge isolation and cultural understanding
- **🛡️ Controlled AI Behavior**: Multi-layer validation and standardized refusal mechanisms
- **⚙️ Production-Grade Engineering**: Comprehensive testing, error handling, and monitoring
- **🔧 Extensible Architecture**: Clean multi-agent design for easy maintenance and enhancement

**Built with ❤️ for the Kiro Heroes Challenge Week 5: The Local Guide**

---

*For technical questions or contributions, please refer to the specification documents in the `docs/` folder or examine the comprehensive test suite in the `testing/` directory.*