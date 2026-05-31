import requests
from convert_exam_notes.llm_parser import md
from colorama import Fore, Style

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

    try:
        resp = requests.post("http://localhost:8765", json=payload).json()
        error_msg: str | None = resp.get("error")
        if error_msg:
            print(Fore.RED + Style.BRIGHT + "\nERROR (from Anki-Connect): \"" + error_msg + '"' + Style.RESET_ALL)
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                print("This error is likely due to the 'PastPaperNote' note type not being created yet. See https://ankiweb.net/shared/info/1969769020")
            elif "deck" in error_msg.lower() and "not found" in error_msg.lower():
                print("Please create the deck in Anki so that this tool may add cards to it.")
    except requests.exceptions.ConnectionError:
        print(Fore.RED + Style.BRIGHT + "\nERROR: Was not able to send cards to Anki." + Style.RESET_ALL)
        print("  This is because either:\n    1) Anki is not installed\n    2) Anki is installed, but not open\n    3) Anki is installed and open, but the Anki-Connect addon hasn't been installed (https://git.sr.ht/~foosoft/anki-connect)")

    # print(f"Added: {card['front'][:60]}...")
