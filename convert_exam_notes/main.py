from argparse import ArgumentParser
import json
import os
import sys
from convert_exam_notes.prompt_llm import get_llm_response
from convert_exam_notes.parser import parse_notes, combine_subject_and_source
from convert_exam_notes.llm_parser import parse_llm_text
from convert_exam_notes.send_to_anki import send_card_to_anki

POSSIBLE_SUBJECTS = [
    "Maths Pure 1 (Paper 1)",
    "Maths Pure 3 (Paper 3)",
    "Maths Mechanics (Paper 4)",
    "Maths Probability & Statistics (Paper 5)",
    "Computer Science Advanced Theory (Paper 3)",
    "Computer Science Practical (Paper 4)",
    "Physics Further Mechanics, Fields and Particles (Paper 4)",
    "Physics Thermodynamics, Radiation, Oscillations and Cosmology (Paper 5)",
    "Physics Practical Skills II (Paper 6)",
]

POSSIBLE_AREAS = ["Maths", "Computer Science", "Physics"]


def save_notes(notes, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=4)


def load_notes(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def upload_cards(notes):
    print(f"\nUploading {len(notes)} cards to Anki...")
    for note in notes:
        send_card_to_anki(note)
    print("Upload complete.")


def generate_cards(notes, area, output_file):
    final_notes = []

    for i, note in enumerate(notes):
        print(f"[{i + 1}/{len(notes)}] Processing note from {note['source']}...")
        paper_general_name = combine_subject_and_source(note, POSSIBLE_SUBJECTS)

        if paper_general_name is not None:
            full_note = f"{paper_general_name}\n{note['content']}"
        else:
            full_note = f"{note['subject']}\n{note['content']}"

        raw_llm_text = get_llm_response(full_note)
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


def main():
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

    args = parser.parse_args()

    if args.anki_only:
        notes = load_notes(args.output)
        if notes is None:
            print(
                f"Error: No cards found at {args.output}. Run without --anki-only first."
            )
            sys.exit(1)
        upload_cards(notes)
        return

    # Subject resolution
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

    # Input resolution
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            input_text = f.read()
    else:
        print("\nEnter your notes (Press Ctrl-D or Ctrl-Z on Windows to finish):")
        input_text = sys.stdin.read()

    if not input_text.strip():
        print("No notes provided. Exiting.")
        return

    notes = parse_notes(input_text, area)
    print(f"\nParsed {len(notes)} notes. Generating flashcards...\n")

    final_notes = generate_cards(notes, area, args.output)
    if (not args.skip_anki): upload_cards(final_notes)


if __name__ == "__main__":
    main()
