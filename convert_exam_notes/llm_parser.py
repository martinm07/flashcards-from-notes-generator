from markdown_it import MarkdownIt
from mdit_py_plugins.texmath import texmath_plugin

import re

# Initialize the parser with GitHub-flavored markdown features
md = (
    MarkdownIt("gfm-like")
    .use(texmath_plugin) # This handles $, $$, \(, and \[
    .enable("table")
)

# 2. Define your Anki-specific rendering functions
def render_anki_inline(self, tokens, idx, options, env):
    # tokens[idx].content contains the raw LaTeX without the $ delimiters
    content = tokens[idx].content
    return f'<anki-mathjax>{content}</anki-mathjax>'

def render_anki_block(self, tokens, idx, options, env):
    content = tokens[idx].content
    # Anki block equations usually don't need a <p> or <section> wrapper
    # unless you want specific spacing.
    return f'<anki-mathjax block="true">{content}</anki-mathjax>'

# 3. Register these rules to override the default plugin output
md.add_render_rule("math_inline", render_anki_inline)
md.add_render_rule("math_block", render_anki_block)

def fix_list_spacing(text: str) -> str:
    list_item = r'[ \t]*(?:[-*+]|\d+\.)[ \t]'

    # Add blank line BEFORE first list item if preceded by a non-empty line
    text = re.sub(rf'(?m)(?<=\S)\n({list_item})', r'\n\n\1', text)

    # Add blank line AFTER last list item if followed by a non-empty line
    text = re.sub(rf'(?m)(^{list_item}.+)\n(?=\S)', r'\1\n\n', text)

    return text


def no_p_markdown(non_p_string) -> str:
    ''' Strip enclosing paragraph marks, <p> ... </p>,
        which markdown() forces, and which interfere with some jinja2 layout
    '''
    return re.sub("(^<P>|</P>$)", "", md.render(non_p_string).strip(), flags=re.IGNORECASE)


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

    front_text = fix_list_spacing(front_text)
    back_text = fix_list_spacing(back_text)

    return {
        "front": no_p_markdown(front_text),
        "back": md.render(back_text),
    }
