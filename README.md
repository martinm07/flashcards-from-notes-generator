# Past Paper Notes Flashcard Generator

Automate the transformation of your exam revision notes—specifically those captured while correcting past papers—into high-quality Anki flashcards using Large Language Models (LLMs).

## Overview

Creating flashcards from study notes is a tedious but essential part of active recall. This tool is specifically designed for students who take notes while reviewing past exam papers. It streamlines the process by taking those loosely formatted notes and using an LLM to intelligently structure them into a "Scenario (Front)" and "Remember (Back)" format. The generated cards are then automatically pushed directly into your Anki decks.

## Key Features

- **Intelligent Flashcard Generation**: Leverages local LLMs (via Ollama/API) to extract key concepts and transform them into effective study prompts.
- **Seamless Anki Integration**: Uses AnkiConnect to automatically populate your Anki decks without manual entry.
- **Smart Organization**: Automatically categorizes cards into subject-specific decks (e.g., `PastPaperNotes::Maths`, `PastPaperNotes::CS`, `PastPaperNotes::Physics`) based on your notes.
- **Flexible Input**: Supports reading notes from files or directly from standard input (`stdin`).
- **Review Workflow**: Saves generated cards to a JSON file, allowing you to review or modify them before committing them to Anki.
- **Robust Parsing**: Handles various note formats, including subject headers and paper identifiers.

## Prerequisites

- **Python 3.13+**
- **Anki** installed and running.
- **AnkiConnect** add-on installed and running in Anki.
- **Local LLM Server**: An Ollama instance (or compatible API) running with a model like `gemma4:26b`.
- **uv**: A fast Python package and project manager.

## Installation

### Option 1: Global Installation (Recommended)
You can install the tool globally using `uv`. This creates a standalone executable named `convert-exam-notes` that is available from your `PATH` (typically in `~/.local/bin` on Linux) without needing to manage a manual virtual environment.

```bash
uv tool install --reinstall .
```

### Option 2: Local Development
If you want to run it within a specific project directory:

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

## Usage

### 1. Prepare your notes
Format your notes using a simple structure. Use headers to denote the source/paper and `- ` for individual notes.

**Example (`notes.txt`):**
```text
Maths Pure 1 (Paper 1)
=======================
- When finding the domain of composed functions, it is NOT the same as taking the intersection of the domains.
- For gf(x), the RANGE of f(x) makes the DOMAIN of g(x).
```

### 2. Generate and Upload
If installed globally, run the command directly:

```bash
convert-exam-notes --input notes.txt
```

If running via `uv run` in the repository:

```bash
uv run convert_exam_notes/main.py --input notes.txt
```

The tool will:
1. Parse your notes.
2. Prompt the LLM to create flashcards.
3. Save the results to `flashcards.json`.
4. Upload the cards to Anki.

### 3. Advanced Commands

- **Skip Anki Upload**: If you only want to generate the JSON file for review:
  ```bash
  convert-exam-notes --input notes.txt --skip-anki
  ```

- **Upload Existing Cards**: If you already have a `flashcards.json` and just want to push it to Anki:
  ```bash
  convert-exam-notes --anki-only
  ```

- **Interactive Mode**: Run without arguments to enter an interactive session where you can select subjects and paste notes directly.

## Project Structure

- `convert_exam_notes/main.py`: The main entry point and CLI logic.
- `convert_exam_notes/parser.py`: Logic for parsing raw text into structured notes.
- `convert_exam_notes/prompt_llm.py`: Handles interaction with the LLM API.
- `convert_exam_notes/llm_parser.py`: Parses the LLM's markdown response into flashcard fields.
- `convert_exam_notes/send_to_anki.py`: Manages the connection to Anki via AnkiConnect.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
