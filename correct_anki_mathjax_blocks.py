import requests
import re
import sys

def replace_anki_mathjax(text: str) -> str:
    r"""
    Replace anki-mathjax tags with LaTeX delimiters:
      <anki-mathjax>           -> \(
      <anki-mathjax block="true"> -> \[
      </anki-mathjax>          -> \) or \] depending on the opening tag
    """
    result = []
    pos = 0
    # Stack to track open tags: 'inline' or 'block'
    stack = []

    # Match any of the three tag forms
    pattern = re.compile(
        r'<anki-mathjax block="true">|<anki-mathjax>|</anki-mathjax>'
    )

    for match in pattern.finditer(text):
        # Append everything between the last match and this one
        result.append(text[pos:match.start()])
        pos = match.end()

        tag = match.group()

        if tag == '<anki-mathjax block="true">':
            stack.append('block')
            result.append(r'\[')
        elif tag == '<anki-mathjax>':
            stack.append('inline')
            result.append(r'\(')
        elif tag == '</anki-mathjax>':
            if stack:
                kind = stack.pop()
                result.append(r'\]' if kind == 'block' else r'\)')
            else:
                # Unmatched closing tag — leave a visible marker
                print("Warning: unmatched </anki-mathjax> tag encountered.",
                      file=sys.stderr)
                result.append(tag)

    # Append any remaining text after the last match
    result.append(text[pos:])

    if stack:
        print(f"Warning: {len(stack)} unclosed <anki-mathjax> tag(s) remaining.",
              file=sys.stderr)

    return "".join(result)


payload = {
    "action": "findNotes",
    "version": 6,
    "params": {
        "query": "deck:PastPaperNotes"
    }
}

resp = requests.post("http://localhost:8765", json=payload)
noteIDs = resp.json()["result"]

# print(noteIDs)

payload = {
    "action": "notesInfo",
    "version": 6,
    "params": {
        "notes": noteIDs
    }
}
resp = requests.post("http://localhost:8765", json=payload)
noteInfos = resp.json()["result"]

# noteInfos = [noteInfos[143]]

def fixField(text: str):
    # print(text)
    # text = text.replace("<anki-mathjax>", "\\(")
    # text = text.replace("</anki-mathjax>", "\\)")
    # text = text.replace('<anki-mathjax block="true">', "\\[")
    text = replace_anki_mathjax(text)
    # print(text)
    # print("\n")
    return text

numNotes = len(noteInfos)

for i, info in enumerate(noteInfos):
    noteID = info["noteId"]
    front = info["fields"]["Front"]["value"]
    back = info["fields"]["Back"]["value"]
    original = info["fields"]["OriginalNote"]["value"]

    newFront = fixField(front)
    newBack = fixField(back)
    newOriginal = fixField(original)

    payload = {
        "action": "updateNoteFields",
        "version": 6,
        "params": {
            "note": {
                "id": noteID,
                "fields": {
                    "Front": newFront,
                    "Back": newBack,
                    "OriginalNote": newOriginal,
                }
            }
        }
    }

    resp = requests.post("http://localhost:8765", json=payload)
    result = resp.json()
    if result["error"] is None:
        print(f"({i+1}/{numNotes}) Successfully updated note of ID {noteID}.")
    else:
        print(f"({i+1}/{numNotes}) FAILED TO UPDATE NOTE OF ID {noteID}")
        print(result)
