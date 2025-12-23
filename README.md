# 🏛️ Local Guide AI

**Production-grade AI assistant for Tamil Nadu cities - Built for Kiro Heroes Challenge Week 5**

A context-driven AI application that provides locality-aware guidance for Madurai and Dindigul using Amazon Nova Premier via Bedrock, with strict hallucination prevention and controlled AI behavior.

## 🎯 What This App Does

Local Guide AI is a specialized AI assistant that provides **accurate, context-driven guidance** for two Tamil Nadu cities: **Madurai** and **Dindigul**. Unlike general-purpose AI assistants, this system:

- **Only uses authoritative local knowledge** stored in markdown context files
- **Refuses to answer** when information isn't available rather than guessing
- **Maintains strict context isolation** between cities
- **Prevents hallucinations** through multi-layer validation
- **Provides practical, local guidance** with Tamil-English mix where appropriate

## 🏗️ Architecture & Context-Driven Design

### Multi-Agent Architecture

The system employs a **four-agent architecture** using the Strands Agents framework:

1. **Context Loader Agent** - Manages city-specific context files
2. **Query Validation Agent** - Validates queries are within supported scope
3. **Local Guide Agent** - Generates responses using Amazon Nova Premier
4. **Guard Agent** - Post-processing validation to prevent hallucinations

### Context Supremacy Principle

The application follows a **context supremacy principle** where:
- All responses must originate from authoritative local knowledge
- No general world knowledge is allowed
- Missing information triggers honest refusal responses
- Context files are the single source of truth

## 📁 Context Files & Kiro Steering

### Why Context Files Matter

Context files (`context/madurai_context.md` and `context/dindigul_context.md`) are the **authoritative source** of local knowledge. They contain:

- **Local food specialties** and restaurant recommendations
- **Transportation options** and routes
- **Local language** and Tamil phrases
- **Safety information** and precautions
- **Cultural practices** and lifestyle information

### How Kiro is Steered Using Documentation

The system uses **documentation-driven steering** through:

1. **System Prompt** (`.kiro/system_prompt.txt`) - Enforces context supremacy and refusal behavior
2. **Context Files** - Provide authoritative local knowledge
3. **Agent Coordination** - Ensures proper information flow and validation
4. **Standardized Refusals** - Maintains consistent behavior when information is unavailable

This approach ensures the AI behaves predictably and provides only verified local information.

## 🚀 How to Run the App Locally

### Prerequisites

- **Python 3.10+**
- **AWS Account** with Bedrock access
- **Amazon Nova Premier** model access enabled

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd local-guide-kiro
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials:**
   
   **Option 1: Bedrock API Key (Recommended for development)**
   ```bash
   export AWS_BEDROCK_API_KEY=your_bedrock_api_key
   ```
   
   **Option 2: AWS Credentials**
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-east-1
   ```

4. **Enable Nova Premier model access:**
   - Go to [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock)
   - Navigate to "Model access" → "Manage model access"
   - Enable "Amazon Nova Premier" model

### Running the Application

**Streamlit Web Interface (Recommended):**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Command Line Interface:**
```bash
python cli_app.py
```

## 💬 Example Queries and Expected Refusals

### ✅ Supported Queries (Will Get Helpful Responses)

**Food & Dining:**
- "Where can I find good biryani in Madurai?"
- "What is Jigarthanda?"
- "Recommend some local restaurants in Dindigul"

**Transport:**
- "How do I get to Meenakshi Temple?"
- "What are the bus routes in the city?"
- "Are auto rickshaws available?"

**Local Language:**
- "What does 'enna da' mean?"
- "How do people greet each other here?"
- "Teach me some Tamil phrases"

**Safety:**
- "Is this area safe at night?"
- "What precautions should I take?"
- "Emergency contact numbers?"

**Lifestyle & Culture:**
- "What festivals are celebrated here?"
- "Tell me about local customs"
- "Where can I shop for traditional items?"

### 🚫 Expected Refusals (Honest "I Don't Know" Responses)

**Out of Scope Topics:**
- "What's the latest political news?" → *"This isn't covered in my local context."*
- "Can you diagnose my medical condition?" → *"I don't have enough local data to answer that."*
- "Help me with programming" → *"My knowledge is limited to what's in the context file."*

**Information Not in Context:**
- "What's the population of Madurai?" → *"This isn't covered in my local context."*
- "When was the temple built?" → *"I don't have enough local data to answer that."*

**General World Knowledge:**
- "What's the weather like in New York?" → *"My knowledge is limited to what's in the context file."*
- "Tell me about global economics" → *"This isn't covered in my local context."*

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