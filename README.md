# Past Paper Notes Flashcard Generator

Automate the transformation of your exam revision notes—specifically those captured while correcting past papers—into Anki flashcards using Large Language Models (LLMs).

## Overview

Creating flashcards from study notes is a tedious but essential part of active recall. This tool is specifically designed for students who take notes while reviewing past exam papers. It streamlines the process by taking those loosely formatted notes and using an LLM to restructure them into a "Scenario (Front)" and "Remember (Back)" format. The generated cards are then automatically pushed directly into your Anki decks.

## Key Features

- **Intelligent Flashcard Generation**: Leverages local LLMs (via Ollama) to extract key concepts and transform them into effective study prompts.
- **Seamless Anki Integration**: Uses AnkiConnect to automatically populate your Anki decks without manual entry.
- **Smart Organization**: Automatically categorizes cards into subject-specific decks (e.g., `PastPaperNotes::Maths`, `PastPaperNotes::CS`, `PastPaperNotes::Physics`) based on your notes.
- **Flexible Input**: Supports reading notes from files or directly from standard input (`stdin`).
- **Review Workflow**: Saves generated cards to a JSON file, and saves logs of the LLM's thought process when making each card, allowing you to review or modify the output before committing them to Anki.
- **Robust Parsing**: Handles various note formats, including subject headers and paper identifiers.

## Prerequisites

- [**Anki**](https://apps.ankiweb.net/) installed and running.
- [**AnkiConnect**](https://git.sr.ht/~foosoft/anki-connect)) add-on installed and running in Anki.
- **Local LLM Server**: An [Ollama](https://ollama.com/) instance (or compatible API) running.

## Installation

### Option 1: Install from pre-built binary

Go to the [releases page](https://github.com/martinm07/flashcards-from-notes-generator/releases/) and install the zip file for your platform (currently limited to Windows and Linux). Unzipping the file will give the binary for the tool, `convert-exam-notes`.

Place this in the system PATH to access the tool from the terminal in any directory.

To run, you can double click on the binary file directly. This will launch a terminal in an interactive session. Alternatively, open a terminal yourself and run via the command-line (this enables more options). To see usage and available options this way run `convert-exam-notes --help`.

### Option 2: Local Development

Clone the repository and run:

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

To run the tool, you can do so via:

```bash
uv run convert_exam_notes/main.py
```


## Usage

### 0. First time running the tool

The tool uses a config file to manage certain behaviours. If it doesn't detect one present (which in all likelihood will be the case on your first run), it initiates an interactive process to scaffold and create this config file. 

The main thing that will need to be done is write out the list of subjects/areas and exams/sub-areas that you will plan to make notes for. While not strictly necessary, it can be good for your own bookeeping and organisation (it will be used to automatically tag generated cards that are sent to Anki, for instance), as well as giving the LLM extra information/context about the notes you feed it.

This list you give will be cross-referenced with the headers denoting sources/papers in your notes (see below), **so make sure they match**. Right now, that is done purely done through the "paper number" i.e. the word "paper" followed by a number. These paper numbers only have to be unique within the subject, as the tool first asks you what subject you're providing notes for. The intention is that these specify the multiple exams you give for each subject. For example, a Maths A-level may have 4 different exams, "Pure 1 (Paper 1)", "Pure 3 (Paper 3), "Mechanics (Paper 4)", and "Probability and Statistics (Paper 5)". When correcting past papers you did, in your notes you specify the exact paper you're correcting (the year and the series it comes from, for instance). The tool can automatically extract the paper number from that, which is useful for the reasons mentioned above. \
What this means:

- Make sure every exam/sub-area entry you specify has a "paper number" in its name (most exams have one naturally)
- Make sure when writing your notes you put them in headings that have a "paper number". 

Also note:

- The config file can be modified at any time. It uses [TOML](https://toml.io).
- The default save location of this config file can be seen when running `convert-exam-notes --help`.
- The location the tool searches for this config file can be changed by passing `--config`. Again, see `convert-exam-notes --help`.

### 1. Prepare your notes
Format your notes using a simple structure. Use headers to denote the source/paper and `- ` for individual notes.

**Example (`notes.txt`):**
```text
Set 2 Paper 1 (June 2025)
=======================
- When finding the domain of composed functions, it is NOT the same as taking the intersection of the domains.
- For gf(x), the RANGE of f(x) makes the DOMAIN of g(x).
```

*Extra info on formatting*: \
*Notes can span multiple lines. A note MUST start with a "-" (a dash) followed with a " " (a space).* \
*Headers are denoted with at LEAST three "-" (dashes) or "=" (equals signs) the line above and/or below the actual heading.*

### 2. Generate and Upload
Open the tool and follow the interactive instructions.

Or, if accessing from the command line, you can run something like

```bash
convert-exam-notes --subject Maths --input notes.txt --model "gemma4:26b"
```

The tool will:
1. Parse your notes.
2. Prompt the LLM to create flashcards.
3. Save the results to `flashcards.json`.
4. Upload the cards to Anki.

### 3. Advanced Commands

- **Skip Anki Upload**: If you only want to generate the JSON file for review:
  ```bash
  convert-exam-notes --subject Maths --input notes.txt --model "gemma4:26b" --skip-anki
  ```

- **Upload Existing Cards**: If you already have a `flashcards.json` and just want to push it to Anki:
  ```bash
  convert-exam-notes --anki-only
  ```

## Project Structure

- `convert_exam_notes/main.py`: The main entry point and CLI logic.
- `convert_exam_notes/parser.py`: Logic for parsing raw text into structured notes.
- `convert_exam_notes/prompt_llm.py`: Handles interaction with the LLM API.
- `convert_exam_notes/llm_parser.py`: Parses the LLM's markdown response into flashcard fields.
- `convert_exam_notes/send_to_anki.py`: Manages the connection to Anki via AnkiConnect.
- `parse_subjects.py`: Handles management of the config file.

## Contribution

Reaching out at `martin.github07@gmail.com` is welcome. Issues and pull requests are welcome. No code of conduct is in place at present, just be civil and sensible :-)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
