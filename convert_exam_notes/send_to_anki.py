import requests
import markdown

def send_card_to_anki(card):
    # 2. Push each card to Anki via AnkiConnect
    final_back = card["back"] + "<div class='original-note'><span>" + markdown.markdown(card["original_note"]) + "</span></div>"

    # print("Live update!")

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "PastPaperNotes",  # change to your deck
                "modelName": "PastPaperNote",
                "fields": {
                    "Front": card["front"],
                    "Back": final_back
                },
                "tags": [tag.replace(" ", "_") for tag in card.get("tags", [])],
                "options": {"allowDuplicate": False}
            }
        }
    }
    requests.post("http://localhost:8765", json=payload)
    # print(f"Added: {card['front'][:60]}...")
