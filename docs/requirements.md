# Requirements Document

## Introduction

The Local Guide AI application is a production-grade, minimal AI system designed for the "Kiro Heroes Challenge – Week 5: The Local Guide". The system provides locality-aware guidance for specific Tamil Nadu cities (Madurai and Dindigul) using context-driven AI behavior with strict hallucination prevention and controlled responses based solely on authoritative local knowledge stored in markdown files.

## Glossary

- **Local Guide System**: The complete AI application that provides city-specific guidance
- **Context File**: Markdown files containing authoritative local knowledge for each supported city
- **Context Loader Agent**: Strands agent responsible for loading the correct city context
- **Query Validation Agent**: Strands agent that validates user queries are within scope
- **Local Guide Agent**: Primary Strands agent using Amazon Nova Premier for response generation
- **Guard Agent**: Safety agent that prevents hallucinations and enforces context-only responses
- **Amazon Nova Premier**: The LLM model accessed via Amazon Bedrock
- **Strands Agents**: The mandatory agent framework for building the AI system
- **Context Supremacy**: The principle that responses must come only from loaded context files
- **Refusal Response**: Standardized responses when information is not available in context

## Requirements

### Requirement 1

**User Story:** As a user, I want to select a specific city (Madurai or Dindigul), so that I can receive locally accurate guidance for that city only.

#### Acceptance Criteria

1. WHEN a user starts the application THEN the Local Guide System SHALL present city selection options for Madurai and Dindigul only
2. WHEN a user selects a city THEN the Context Loader Agent SHALL load only that city's corresponding context file
3. WHEN a city is selected THEN the Local Guide System SHALL prevent mixing of context data from other cities
4. WHEN a user switches cities THEN the Context Loader Agent SHALL reload the new city's context and clear previous context
5. WHERE the application provides a user interface THEN the Local Guide System SHALL display the currently selected city clearly

### Requirement 2

**User Story:** As a user, I want to ask natural language questions about local topics, so that I can get practical guidance based on authoritative local knowledge.

#### Acceptance Criteria

1. WHEN a user submits a query about food, transport, slang, safety, or lifestyle THEN the Query Validation Agent SHALL accept the query for processing
2. WHEN a user submits a query outside the supported scope THEN the Query Validation Agent SHALL reject the query with appropriate messaging
3. WHEN a valid query is processed THEN the Local Guide Agent SHALL generate responses using only the loaded context file content
4. WHEN generating responses THEN the Local Guide Agent SHALL use Amazon Nova Premier via Amazon Bedrock
5. WHEN responding THEN the Local Guide System SHALL maintain a local, practical tone with Tamil-English mix where context supports it

### Requirement 3

**User Story:** As a user, I want the AI to refuse to answer when information is not available in the context, so that I receive only accurate and verified local information.

#### Acceptance Criteria

1. WHEN the Local Guide Agent cannot find relevant information in the context file THEN the Local Guide System SHALL provide a standardized refusal response
2. WHEN refusing to answer THEN the Local Guide System SHALL use only one of these exact phrases: "This isn't covered in my local context.", "I don't have enough local data to answer that.", or "My knowledge is limited to what's in the context file."
3. WHEN generating any response THEN the Guard Agent SHALL validate that no information outside the context file is included
4. IF the Guard Agent detects hallucination or external knowledge THEN the Local Guide System SHALL force a refusal response
5. WHEN uncertain about information THEN the Local Guide System SHALL prefer refusal over guessing or inference

### Requirement 4

**User Story:** As a user, I want to interact with the system through a simple interface, so that I can easily access local guidance without complexity.

#### Acceptance Criteria

1. WHERE the system uses Streamlit THEN the Local Guide System SHALL provide a dropdown for city selection, text input for questions, and clear response display
2. WHERE the system uses CLI THEN the Local Guide System SHALL prompt for city selection and accept text input with clean response printing
3. WHEN displaying responses THEN the Local Guide System SHALL show refusal messages clearly and distinctly
4. WHEN the application starts THEN the Local Guide System SHALL be immediately usable without authentication, database setup, or logging configuration
5. WHEN users interact with the interface THEN the Local Guide System SHALL provide clear feedback for all actions

### Requirement 5

**User Story:** As a developer, I want the system to use the specified tech stack and architecture, so that it meets the challenge requirements and demonstrates proper engineering practices.

#### Acceptance Criteria

1. WHEN implementing the system THEN the Local Guide System SHALL use Python 3.10+, Strands Agents framework, and Amazon Bedrock with Nova Premier
2. WHEN storing local knowledge THEN the Local Guide System SHALL use markdown files in the context directory structure
3. WHEN processing queries THEN the Local Guide System SHALL implement exactly four Strands agents: Context Loader, Query Validation, Local Guide, and Guard agents
4. WHEN enforcing behavior THEN the Local Guide System SHALL inject a strict system prompt that enforces context supremacy and prevents hallucination
5. WHEN deployed THEN the Local Guide System SHALL run locally without external dependencies beyond the specified tech stack

### Requirement 6

**User Story:** As a system administrator, I want the application to have a clear project structure and documentation, so that it can be easily understood, maintained, and deployed.

#### Acceptance Criteria

1. WHEN the project is created THEN the Local Guide System SHALL follow the specified directory structure with agents, context, and configuration files
2. WHEN documenting the system THEN the Local Guide System SHALL include a comprehensive README explaining functionality, context file importance, and local execution instructions
3. WHEN providing context files THEN the Local Guide System SHALL include madurai_context.md and dindigul_context.md with authoritative local knowledge
4. WHEN configuring the system THEN the Local Guide System SHALL include requirements.txt with all necessary dependencies
5. WHEN explaining the system THEN the Local Guide System SHALL document example queries and expected refusal scenarios