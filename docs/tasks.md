# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure: /agents, /context, root files
  - Create requirements.txt with Strands Agents, Streamlit, and dependencies
  - Create .kiro/system_prompt.txt with strict context enforcement prompt
  - _Requirements: 5.1, 5.2, 6.1, 6.4_

- [x] 2. Create context files and data models
  - [x] 2.1 Create context files with local knowledge
    - Write context/madurai_context.md with authoritative local information
    - Write context/dindigul_context.md with authoritative local information
    - _Requirements: 6.3_

  - [x] 2.2 Implement core data models
    - Write CityContext, Query, Response, and AppState dataclasses
    - Implement validation methods and utility functions
    - _Requirements: 1.2, 2.1, 3.1_

  - [x] 2.3 Write property test for context isolation
    - **Property 1: Context isolation and loading**
    - **Validates: Requirements 1.2, 1.3, 1.4**

- [x] 3. Implement Context Loader Agent
  - [x] 3.1 Create Context Loader Agent with Strands framework
    - Implement load_city_context, get_available_cities, validate_city_selection methods
    - Configure agent with appropriate system prompt for context loading
    - _Requirements: 1.2, 1.3, 1.4_

  - [x] 3.2 Write unit tests for Context Loader Agent
    - Test context file loading for both cities
    - Test context isolation and switching behavior
    - Test error handling for missing or malformed files
    - _Requirements: 1.2, 1.3, 1.4_

- [x] 4. Implement Query Validation Agent
  - [x] 4.1 Create Query Validation Agent with scope checking
    - Implement validate_query_scope, get_rejection_reason, is_supported_topic methods
    - Configure agent to recognize supported topics (food, transport, slang, safety, lifestyle)
    - _Requirements: 2.1, 2.2_

  - [x] 4.2 Write property test for query validation
    - **Property 2: Query scope validation**
    - **Validates: Requirements 2.1, 2.2**

  - [x] 4.3 Write unit tests for Query Validation Agent
    - Test acceptance of supported topic queries
    - Test rejection of out-of-scope queries
    - Test edge cases with empty or malformed queries
    - _Requirements: 2.1, 2.2_

- [x] 5. Implement Local Guide Agent with Nova Premier
  - [x] 5.1 Create Local Guide Agent using Amazon Bedrock
    - Configure BedrockModel with Nova Premier (us.amazon.nova-premier-v1:0)
    - Implement generate_response method with strict context adherence
    - Apply system prompt for context-only responses and local tone
    - _Requirements: 2.3, 2.4, 5.1_

  - [x] 5.2 Write property test for context-only responses
    - **Property 3: Context-only response generation**
    - **Validates: Requirements 2.3**

  - [x] 5.3 Write unit tests for Local Guide Agent
    - Test response generation with valid context
    - Test model configuration and Bedrock integration
    - Test system prompt application and enforcement
    - _Requirements: 2.3, 2.4_

- [x] 6. Implement Guard Agent for hallucination prevention
  - [x] 6.1 Create Guard Agent with validation logic
    - Implement validate_response, detect_hallucination, force_refusal methods
    - Configure agent to detect external knowledge and enforce refusals
    - _Requirements: 3.3, 3.4_

  - [x] 6.2 Write property test for guard validation
    - **Property 5: Guard agent validation**
    - **Validates: Requirements 3.3, 3.4**

  - [x] 6.3 Write unit tests for Guard Agent
    - Test validation of context-only responses
    - Test detection of hallucinated content
    - Test forced refusal mechanisms
    - _Requirements: 3.3, 3.4_

- [x] 7. Implement refusal response system
  - [x] 7.1 Create standardized refusal response handler
    - Implement logic to generate standardized refusal phrases
    - Ensure only approved refusal messages are used
    - _Requirements: 3.1, 3.2_

  - [x] 7.2 Write property test for standardized refusals
    - **Property 4: Standardized refusal responses**
    - **Validates: Requirements 3.1, 3.2**

  - [x] 7.3 Write unit tests for refusal system
    - Test generation of standardized refusal phrases
    - Test refusal triggering conditions
    - Test refusal message consistency
    - _Requirements: 3.1, 3.2_

- [x] 8. Create agent orchestration and main application logic
  - [x] 8.1 Implement agent coordination system
    - Create main application class that coordinates all four agents
    - Implement processing pipeline: Context Loading → Query Validation → Response Generation → Guard Validation
    - Handle error propagation and fallback behaviors
    - _Requirements: 5.3_

  - [ ] 8.2 Write integration tests for agent pipeline
    - Test end-to-end processing flow
    - Test error handling and recovery
    - Test agent interaction patterns
    - _Requirements: 5.3_

- [ ] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement Streamlit user interface
  - [x] 10.1 Create Streamlit app with required components
    - Implement city selection dropdown with Madurai and Dindigul options
    - Create text input for user questions
    - Design clear response display area with refusal message highlighting
    - _Requirements: 4.1, 4.3_

  - [ ] 10.2 Write unit tests for Streamlit interface
    - Test UI component rendering and interaction
    - Test city selection and state management
    - Test response display formatting
    - _Requirements: 4.1, 4.3_

- [x] 11. Implement CLI interface as alternative
  - [x] 11.1 Create CLI interface with prompts and clean output
    - Implement city selection prompts
    - Create text input handling with clean response printing
    - Format refusal messages clearly in CLI output
    - _Requirements: 4.2, 4.3_

  - [ ] 11.2 Write unit tests for CLI interface
    - Test CLI prompts and input handling
    - Test response formatting and display
    - Test error message presentation
    - _Requirements: 4.2, 4.3_

- [ ] 12. Add comprehensive error handling
  - [ ] 12.1 Implement error handling for all failure modes
    - Add context loading error handling (file not found, permissions, malformed content)
    - Add model integration error handling (Bedrock connection, authentication, rate limiting)
    - Add query processing error handling (empty queries, special characters, length limits)
    - _Requirements: 5.5_

  - [ ] 12.2 Write unit tests for error handling
    - Test all error conditions and recovery mechanisms
    - Test error message clarity and user guidance
    - Test system stability under error conditions
    - _Requirements: 5.5_

- [x] 13. Create comprehensive documentation
  - [x] 13.1 Write comprehensive README.md
    - Explain application functionality and context-driven behavior
    - Document context file importance and Kiro steering principles
    - Provide local execution instructions and setup guide
    - Include example queries and expected refusal scenarios
    - _Requirements: 6.2, 6.5_

  - [ ] 13.2 Create system configuration documentation
    - Document .kiro/system_prompt.txt usage and importance
    - Explain agent architecture and interaction patterns
    - Provide troubleshooting guide for common issues
    - _Requirements: 5.4, 6.2_

- [ ] 14. Final integration and deployment preparation
  - [ ] 14.1 Ensure local deployment readiness
    - Verify system runs without external dependencies beyond tech stack
    - Test immediate usability without authentication or database setup
    - Validate all components work together seamlessly
    - _Requirements: 4.4, 5.5_

  - [ ] 14.2 Write end-to-end integration tests
    - Test complete user workflows from city selection to response
    - Test system behavior under various usage patterns
    - Test performance and resource usage
    - _Requirements: 4.4, 5.5_

- [ ] 15. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.