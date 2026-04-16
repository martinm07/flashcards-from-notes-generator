import markdown
import re


def no_p_markdown(non_p_string) -> str:
    ''' Strip enclosing paragraph marks, <p> ... </p>,
        which markdown() forces, and which interfere with some jinja2 layout
    '''
    return re.sub("(^<P>|</P>$)", "", markdown.markdown(non_p_string), flags=re.IGNORECASE)


def parse_llm_text(raw: str):
    match = re.search(
        r"# Front\s*(.*?)\s*# Back\s*(.*)", raw, re.DOTALL | re.IGNORECASE
    )

    if match:
        front_text = match.group(1).strip()
        back_text = match.group(2).strip()
    else:
        front_text = "[Error: Front header missing]"
        back_text = "[Error: Back header missing]"
        if not raw:
            front_text = "[Error: Empty response]"
            back_text = "[Error: Empty response]"

    return {
        "front": no_p_markdown(front_text),
        "back": markdown.markdown(back_text),
    }
