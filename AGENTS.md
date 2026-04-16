# AGENTS.md

This document provides essential information for any agentic coding agent working in this repository.

## Project Focus

This is a simple Python project to take in a list of (loosely formatted) notes, pass each one through an LLM to turn into a flashcard, and then automatically add them to an Anki deck.

## Build, Lint, and Test Commands

Currently, this project is a simple Python script and does not have a formal build or test suite.

- **Running the application**:
  ```bash
  python main.py
  ```

### Python Conventions
- **Imports**: Group imports by standard library, then third-party libraries, then local modules.
- **Formatting**: Follow PEP 8. Use 4 spaces for indentation.
- **Typing**: Use type hints for function signatures where possible (e.g., `def func(param: str) -> str:`).
- **Naming**:
  - Variables and functions: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Classes: `PascalCase`
- **Error Handling**:
  - Use specific exceptions instead of broad `except Exception:`.
  - For API calls (like `requests.post`), handle potential network errors or non-200 status codes.
- **Documentation**:
  - Use docstrings for complex functions.
  - Maintain the existing style of using triple-quoted strings for large text blocks (like `SYSTEM_PROMPT`).

### Prompt Engineering & LLM Interaction
- **System Prompts**: NEVER modify `SYSTEM_PROMPT`, only the user is allowed to do that. If you have suggested modifications, tell them to the user and they will consider them.
- **Few-Shot Examples**: DON'T add new examples or modify existing examples. If you have suggested modifications, tell them to the user and they will consider them.

## Project Structure
- `main.py`: Entry point of the application.
- `prompt_llm.py`: Contains the logic for interacting with the LLM and managing prompts.
- `log/`: Directory where LLM thinking process and raw responses are logged.
