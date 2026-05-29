from argparse import ArgumentParser
import json
import os
import sys
import requests
import toml
from pathlib import Path
from convert_exam_notes.prompt_llm import get_llm_response
from convert_exam_notes.parser import parse_notes, combine_subject_and_source
from convert_exam_notes.llm_parser import parse_llm_text
from convert_exam_notes.send_to_anki import send_card_to_anki
from convert_exam_notes.parse_subjects import create_toml_config, get_config_dir, parse_subjects, toml_config_to_subject_lists

# POSSIBLE_SUBJECTS = [
#     "Maths Pure 1 (Paper 1)",
#     "Maths Pure 3 (Paper 3)",
#     "Maths Mechanics (Paper 4)",
#     "Maths Probability & Statistics (Paper 5)",
#     "Computer Science Advanced Theory (Paper 3)",
#     "Computer Science Practical (Paper 4)",
#     "Physics Further Mechanics, Fields and Particles (Paper 4)",
#     "Physics Thermodynamics, Radiation, Oscillations and Cosmology (Paper 5)",
#     "Physics Practical Skills II (Paper 6)",
# ]

# POSSIBLE_AREAS = ["Maths", "Computer Science", "Physics"]

POSSIBLE_SUBJECTS: list[str]
POSSIBLE_AREAS: list[str]


def save_notes(notes, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=4)


def load_notes(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def upload_cards(notes, config):
    print(f"\nUploading {len(notes)} cards to Anki...")
    for note in notes:
        send_card_to_anki(note, config)
    print("Upload complete.")


def generate_cards(notes, area, output_file, model: str, port: int):
    final_notes = []

    for i, note in enumerate(notes):
        print(f"[{i + 1}/{len(notes)}] Processing note from {note['source']}...")
        paper_general_name = combine_subject_and_source(note, POSSIBLE_SUBJECTS)

        if paper_general_name is not None:
            full_note = f"{paper_general_name}\n{note['content']}"
        else:
            full_note = f"{note['subject']}\n{note['content']}"

        raw_llm_text = get_llm_response(full_note, model, port)
        parsed_llm_text = parse_llm_text(raw_llm_text)

        final_notes.append(
            {
                "front": parsed_llm_text["front"],
                "back": parsed_llm_text["back"],
                "full_note": full_note,
                "original_note": note["content"],
                "tags": [
                    tag
                    for tag in [note["subject"], paper_general_name, note["source"]]
                    if tag is not None
                ],
            }
        )

        save_notes(final_notes, output_file)

    return final_notes


def scaffold_config(args, model_names):
    print(f"No '{str(args.config)}' file found. Scaffolding a new one (Press Ctrl-C to escape).\n")

    print(f"Create headings for your different subjects/areas, and under each heading list your exams/sub-areas.\nAn example is below:")
    print(f"==================== '{str(args.config)}':")
    print("""[Maths]
Maths Pure 1 (Paper 1)
Maths Pure 3 (Paper 3)
Maths Mechanics (Paper 4)
Maths Probability & Statistics (Paper 5)

[Computer Science]
Computer Science Advanced Theory (Paper 3)
Computer Science Practical (Paper 4)

[Physics]
Physics Further Mechanics, Fields and Particles (Paper 4)
Physics Thermodynamics, Radiation, Oscillations and Cosmology (Paper 5)
Physics Practical Skills II (Paper 6)""")
    print("====================")
    print(f"\nNow enter below the contents for your '{str(args.config)}' (Press Ctrl-D, or Ctrl-Z and Enter on Windows, to finish):")
    input_text = sys.stdin.read()

    final_config = {}

    try:
        parsed = parse_subjects(input_text)
        final_config["subject"] = create_toml_config(parsed)
        print("...Set")
    except:
        print("\nError while parsing!")
        return

    print("\nFor Anki integration, we will create subdecks for all your subjects/areas under a common name. What should this common name be?")

    while True:
        user_resp = input("Enter name: ")
        if not user_resp:
            print("Oops, missing name.")
        else:
            main_anki_deckname = user_resp.replace(" ", "") # TODO: More santization/validation
            final_config["anki-main-deckname"] = main_anki_deckname
            print("...Set")
            break


    print("\nWhile we're at it, is there a specific model you'd like to use for all LLM generation?")
    preferred_llm_model = input("Enter model name (Leave blank to skip): ")
    if preferred_llm_model:
        if model_names is not None and preferred_llm_model not in model_names:
            print(f"WARNING: '{preferred_llm_model}' was not in the list of detected models.")

        final_config["default-llm-model"] = preferred_llm_model
        print("...Set")

    print("\nAll done.")

    path = Path(str(args.config))
    os.makedirs(path.parent)
    with open(str(args.config), "w") as f:
        toml.dump(final_config, f)
    print(f"...Created and populated '{str(args.config)}'.")
    return True


def main():
    global POSSIBLE_SUBJECTS, POSSIBLE_AREAS

    parser = ArgumentParser(
        description="Generate Anki flashcards from notes using LLM."
    )
    parser.add_argument(
        "-s", "--subject", help="Subject/Area (e.g., Maths, Computer Science, Physics)"
    )
    parser.add_argument(
        "-i", "--input", help="Path to input notes file. Reads from stdin if omitted."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="flashcards.json",
        help="Path to save generated cards (default: flashcards.json)",
    )

    default_config_path = f"{get_config_dir() / "config.toml"}"
    parser.add_argument(
        "--config",
        default=default_config_path,
        help=f"Path to file listing subject/exam names that you are writing notes for (default: {default_config_path})"
    )

    parser.add_argument(
        "-m",
        "--model",
        help="The name of the LLM model, to be passed to Ollama (e.g. 'gemma4:26b')"
    )

    parser.add_argument(
        "--anki-only",
        action="store_true",
        help="Skip LLM generation and upload existing cards from output file to Anki",
    )
    parser.add_argument(
        "--skip-anki",
        action="store_true",
        help="Skip sending cards to Anki, and focus only on LLM generation",
    )

    parser.add_argument(
        "--ollama-port",
        type=int,
        help="Specify the port the Ollama runner is listening on (default: 11434)",
        default=11434
    )

    args = parser.parse_args()

    # Check Ollama connection and get (and print) valid model names

    try:
        response = requests.get(f"http://localhost:{args.ollama_port}/api/tags")

        model_names = [entry["name"] for entry in response.json()["models"]]
        print(f"\nDetected the following models: {', '.join([f"'{name}'" for name in model_names])}\n")

        # Ollama generally seems to give all model names of the form "[modelname]:[ver]" and when querying a model, Ollama will happily accept just the "[modelname]" (and it will choose the specific version itself)
        # So, this is to add the "[modelname]"s as other valid options
        model_name_stems = list(set([name.split(":")[0] for name in model_names]))
        model_names.append(*model_name_stems)

    except requests.exceptions.ConnectionError:
        print("\nWARNING: Could not connect to the Ollama server! Either:\n1) Ollama is not installed\n2) Ollama is installed, but is not running (run `ollama serve` in a terminal)\n3) Ollama is installed and running, but not on port 11434 (pass in --ollama-port to specify the correct port for this command)\n")
        model_names = None

    # Config loading / scaffolding

    if not os.path.exists(str(args.config)):
        result = scaffold_config(args, model_names)
        if not result:
            return

    with open(str(args.config), "r") as f:
        config = toml.load(f)
        POSSIBLE_AREAS, POSSIBLE_SUBJECTS = toml_config_to_subject_lists(config)



    if args.anki_only:
        notes = load_notes(args.output)
        if notes is None:
            print(
                f"Error: No cards found at {args.output}. Run without --anki-only first."
            )
            sys.exit(1)
        upload_cards(notes, config)
        return


    area = args.subject
    if not area:
        print("\nPossible subjects:")
        for i, s in enumerate(POSSIBLE_AREAS):
            print(f"{i + 1}. {s}")

        subject_input = input("\nEnter subject (number or name): ").strip()
        if subject_input.isdigit():
            idx = int(subject_input) - 1
            if 0 <= idx < len(POSSIBLE_AREAS):
                area = POSSIBLE_AREAS[idx]
            else:
                area = subject_input
        else:
            area = subject_input

    model_name = args.model or config.get("default-llm-model")
    while not model_name:
        user_resp = input("Enter the name of the LLM model, to be passed to Ollama (e.g. 'gemma4:26b'): ")
        if model_names is not None and user_resp not in model_names:
            print(f"WARNING: '{user_resp}' was not in the list of detected models.")
        model_name = user_resp
    else:
        print(f"Autoselected model of name '{model_name}'.")

    # Input resolution
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            input_text = f.read()
    else:
        print("\nEnter your notes (Press Ctrl-D, or Ctrl-Z and Enter on Windows, to finish):")
        input_text = sys.stdin.read()

    if not input_text.strip():
        print("No notes provided. Exiting.")
        return

    notes = parse_notes(input_text, area)
    print(f"\nParsed {len(notes)} notes. Generating flashcards...\n")

    final_notes = generate_cards(notes, area, args.output, model_name, args.ollama_port)
    if (not args.skip_anki): upload_cards(final_notes, config)


if __name__ == "__main__":
    main()
