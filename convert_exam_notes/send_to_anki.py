import requests
import markdown

def send_card_to_anki(card):
    # 2. Push each card to Anki via AnkiConnect
    final_back = card["back"]

    tags = card.get("tags", [])
    if "Maths" in tags: deckName = "PastPaperNotes::Maths"
    elif "Computer Science" in tags: deckName = "PastPaperNotes::CS"
    elif "Physics" in tags: deckName = "PastPaperNotes::Physics"
    else: deckName = "PastPaperNotes"

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
                    "OriginalNote": markdown.markdown(card["original_note"])
                },
                "tags": [tag.replace(" ", "_") for tag in card.get("tags", [])],
                "options": {"allowDuplicate": False}
            }
        }
    }
    requests.post("http://localhost:8765", json=payload)
    # print(f"Added: {card['front'][:60]}...")
