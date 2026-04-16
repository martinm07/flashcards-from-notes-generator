import re
from typing import List, Dict
import warnings

DEBUG = False

def parse_notes(text: str, subject: str) -> List[Dict[str, str]]:
    """
    Parses loosely formatted notes into a list of individual notes.
    """
    lines = text.splitlines()
    sections = []
    current_source = "Unknown"
    if (DEBUG): print(f"🎈 (initial) CHANGING current_source, to '{current_source}'")
    current_block = []

    i = 0
    while i < len(lines):
        line = lines[i]

        is_delimiter = re.match(r"^[=-]{3,}$", line)

        # Case 1: Delimiter on top
        # [Delimiter] -> [Title] -> [Optional Delimiter]
        if is_delimiter:
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Title line can have optional symbols at start/end
                if re.match(r"^[=-]*\s*.+?\s*[=-]*$", next_line):
                    if current_block:
                        sections.append(
                            {
                                "source": current_source,
                                "content": "\n".join(current_block),
                            }
                        )

                    title = next_line.strip("=- ").strip()
                    current_source = title
                    if (DEBUG): print(f"🎈 (case 1) CHANGING current_source, to '{current_source}'")
                    current_block = []
                    i += 2
                    if i < len(lines) and re.match(r"^[=-]{3,}$", lines[i]):
                        i += 1
                    continue

        # Case 2: Title first, then delimiter below
        # [Title] -> [Delimiter]
        # To avoid confusing notes with titles, we only treat this as a title if:
        # 1. It doesn't start with "- " (the note pattern)
        # 2. OR it ends with a delimiter character (suggesting it's a styled title)
        if line.strip("=- ").strip() != "" and not is_delimiter:
            if i + 1 < len(lines) and re.match(r"^[=-]{3,}$", lines[i + 1]):
                # Check if it's a title or just a note followed by a section delimiter
                is_note_pattern = line.startswith("- ")
                is_styled_title = line.strip().endswith(("-", "="))

                if not is_note_pattern or is_styled_title:
                    if current_block:
                        sections.append(
                            {
                                "source": current_source,
                                "content": "\n".join(current_block),
                            }
                        )

                    title = line.strip("=- ").strip()
                    current_source = title
                    if (DEBUG): print(f"🎈 (case 2) CHANGING current_source, to '{current_source}'")
                    current_block = []
                    i += 2
                    continue

        # Check for Paper-specific Header
        if re.search(r"Paper\s+\d+", line, re.IGNORECASE):
            if current_block:
                sections.append(
                    {"source": current_source, "content": "\n".join(current_block)}
                )

            current_source = line.strip()
            if (DEBUG): print(f"🎈 (paper-specific header) CHANGING current_source, to '{current_source}'")
            current_block = []
            i += 1
            if i < len(lines) and re.match(r"^[=-]{3,}$", lines[i]):
                i += 1
            continue

        current_block.append(line)
        i += 1

    if current_block:
        sections.append({"source": current_source, "content": "\n".join(current_block)})

    if (DEBUG): print(sections)

    all_notes = []
    for section in sections:
        source = section["source"]
        content = section["content"]
        content = "\n" + content
        parts = re.split(r"(?=\n- )", content)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if part.startswith("- "):
                note_text = part[2:].strip()
            elif part.startswith("\n- "):
                note_text = part[2:].strip()
            else:
                continue

            if "everything correct" in note_text.lower():
                continue
            if "full marks" in note_text.lower():
                continue
            if "🎉" in note_text.lower():
                continue

            if note_text:
                all_notes.append(
                    {"subject": subject, "source": source, "content": note_text}
                )

    return all_notes

def combine_subject_and_source(note: dict[str, str], possible_subjects: list[str]):
    subject = note["subject"] # e.g. "Computer Science"
    source = note["source"] # e.g. Set 1 Paper 3 (June 2021)

    filtered_subjects = [subject_ for subject_ in possible_subjects if subject.lower().replace(" ", "") in subject_.lower().replace(" ", "")]
    source_paper = re.search("paper *(\\d+)", source.lower())

    # print("◆◆◆ Subject: ", subject)
    # print("◆◆◆ Source: ", source)

    if source_paper is None:
        # print("🎈🎈 no paper detected in source")
        return None

    paper_number = source_paper.group(1)
    # print("🎈🎈 Detected paper number: ", paper_number)
    # print("🎈🎈 filtered subjects:", filtered_subjects)

    final_possible_subject = [subject for subject in filtered_subjects if f"paper{paper_number}" in subject.lower().replace(" ", "")]
    if len(final_possible_subject) > 1:
        warnings.warn(f"More than one possible subject was identified for subject '{subject}' and source '{source}'")
        print("🎈🎈 final possible subjects:", final_possible_subject)
    elif len(final_possible_subject) == 0:
        # print("🎈🎈 narrowed possible subjects to 0")
        return None

    return final_possible_subject[0]
