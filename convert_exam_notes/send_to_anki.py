import requests
from convert_exam_notes.llm_parser import md

def send_card_to_anki(card, config: dict):
    # 2. Push each card to Anki via AnkiConnect
    final_back = card["back"]

    main_deckname = config["anki-main-deckname"] or "PastPaperNotes"

    tags = card.get("tags", [])

    # if "Maths" in tags: deckName = f"{main_deckname}::Maths"
    # elif "Computer Science" in tags: deckName = f"{main_deckname}::CS"
    # elif "Physics" in tags: deckName = f"{main_deckname}::Physics"
    # else: deckName = f"{main_deckname}"

    for subject in config["subject"]:
        if subject["name"] in tags:
            deckName = f"{main_deckname}::{subject['anki-deckname']}"
            break
    else:
        deckName = f"{main_deckname}"

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deckName,  # change to your deck
                "modelName": "PastPaperNote",
                "fields": {
                    "Front": card["front"],
                    "Back": final_back,
                    "OriginalNote": md.render(card["original_note"])
                },
                "tags": [tag.replace(" ", "_") for tag in card.get("tags", [])],
                "options": {"allowDuplicate": False}
            }
        }
    }
    requests.post("http://localhost:8765", json=payload)
    # print(f"Added: {card['front'][:60]}...")
