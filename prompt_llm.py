import requests, json, os

SYSTEM_PROMPT = """<|think|>
You are helping a student prepare for exams by rewriting the notes they make when correcting past papers into a flashcard format, for them to later review.
You have wide knowledge of the subject the student is revising, but respect the student's notes and so mainly focus on the pure task of adapting them to the flashcard format.

**Your Approach to Writing the Card**
- The front of the card names a SCENARIO that may come up in an exam, where the point raised in the provided note would become relevant.
- The back of the card gives the REMINDER, which is what was set out in the provided note.

**How You Structure Your Responses**
- You use markdown. You can't use LaTeX maths equations.
- The front and back of the flashcard are delineated with H1 headings.
- You EXACTLY write "# Front", then a couple of new lines, then the content for the front of the card.
- Then after a couple more newlines, you do the same for the back of the card, writing EXACTLY "# Back".
- YOU DON'T WRITE ANYTHING ELSE IN YOUR RESPONSE― ONLY THE FLASHCARD.
- To become confident in what you will write for the flashcard, use thinking. The MOMENT you are REASONABLY confident with what you'll generally include, stop thinking and start writing the flashcard.
- DON'T USE THINKING to plan exact sentence structures, or phrasings.

**Some additional guidance from the student:**

On preserving underlying information:
- Retain 100% information I write down in the flashcard. DO NOT modify or add extra information.
- If you KNOW something about the note is missing or incorrect, add a comment to the end of the back of the card, on a paragraph that begins with "**Ai comment:** ".

***

WHAT FOLLOWS IS THE CONVERSATION SO FAR (clipped to the latest context).
"""

ex_note_1 = """Pure Maths 1 (Paper 1)
When finding the domain of composed functions, it is NOT the same as taking the intersection of the domains of the two functions being composed― for gf(x), the RANGE of f(x) makes the DOMAIN of g(x); the domain of gf(x) must be found through analysis, but will be a subset of the domain of f(x), specifically, the subset of values that make results within the domain of g(x)."""

ex_resp_1 = """# Front

You are finding the domain of a composed function gf(x)

# Back

It is NOT the same as taking the intersection of the domains of the functions being composed.
For gf(x), the RANGE of f(x) makes the DOMAIN of g(x). Hence, the domain of gf(x) will be a *subset* of the domain of f(x). Specifically, the subset of values that make results within the domain of g(x). (*This must be determined through analysis of the actual functions.*)"""

ex_note_2 = """Computer Science Advanced Theory (Paper 3)
The "purpose" of user-defined data types is NOT to "better organise data" in programs, and NOT to "mimick real-world entities". Think much more basic― the purpose is to "create a new data type, from existing data types". Think about it from the perspective of the programming language, not the programmer― to "allow data types *not available* to be constructed -> to extend FLEXIBILITY of the programming language". Flexbility is a good anchor word for user-defined data types."""

ex_resp_2 = """# Front

You are explaining the purpose of user-defined data types

# Back

It is NOT to "better organise data" in programs, nor to "mimick real-world entities". You instead think "flexibility".
And instead of answering from the user perspective, consider if it should be answered from the *perspective of the programming language*, where the purpose is simply that they allow "the creation of new data types, from existing data types," allowing data types *not available* in the language to be constructed → extending **FLEXIBILITY** of the programming language."""

ex_note_3 = """Maths Mechanics (Paper 4)
Given we know the overall acceleration of a set of connected objects, we can just use one of the objects to figure stuff out. We do NOT need to find the expressions for the accelerations of each and equate them."""

ex_resp_3 = """# Front

You know the overall acceleration of a set of connected objects, and are finding the tension in the tow-bar connecting them

# Back

It is NOT necessary to find the expressions for the acceleration of each object and equate them.
You can just find the expression for acceleration of one object and equate it to the known acceleration."""


def get_llm_response(note: str):
    # There is also the API endpoint http://localhost:11434/api/generate
    #  which is just for a single prompt (+ a system prompt), but that doesn't properly expose "thinking support" apparently.
    response = requests.post("http://localhost:11434/api/chat", json={
        # "model": "gemma4:31b",
        "model": "gemma4:26b",
        "think": True,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": "The student has provided the 72nd note for you to adapt:"},
            {"role": "user", "content": ex_note_1},
            {"role": "assistant", "content": ex_resp_1},
            {"role": "system", "content": "The student has provided the 73rd note for you to adapt:"},
            {"role": "user", "content": ex_note_2},
            {"role": "assistant", "content": ex_resp_2},
            {"role": "system", "content": "The student has provided the 74th note for you to adapt:"},
            {"role": "user", "content": ex_note_3},
            {"role": "assistant", "content": ex_resp_3},
            {"role": "system", "content": "The student has provided the 75th note for you to adapt:"},
            {"role": "user", "content": note}
        ]
    })

    data = response.json()
    thinking = data["message"].get("thinking", "")
    raw      = data["message"]["content"]

    i = 1
    while os.path.exists(f"log/{i}.txt"): i += 1

    with open(f"log/{i}.txt", "w+") as f:
        f.write('"""' + thinking + '"""')
        f.write("\n\n==========\n\n")
        f.write('"""' + raw + '"""')

    return raw


# cards = json.loads(raw)  # list of {front, back}

# # 2. Push each card to Anki via AnkiConnect
# for card in cards:
#     payload = {
#         "action": "addNote",
#         "version": 6,
#         "params": {
#             "note": {
#                 "deckName": "Maths::Error Log",  # change to your deck
#                 "modelName": "Basic",
#                 "fields": {
#                     "Front": card["front"],
#                     "Back": card["back"]
#                 },
#                 "options": {"allowDuplicate": False}
#             }
#         }
#     }
#     requests.post("http://localhost:8765", json=payload)
#     print(f"Added: {card['front'][:60]}...")
