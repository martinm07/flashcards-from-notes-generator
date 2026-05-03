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
    return f'\\({content}\\)'

def render_anki_block(self, tokens, idx, options, env):
    content = tokens[idx].content
    # Anki block equations usually don't need a <p> or <section> wrapper
    # unless you want specific spacing.
    return f'\\[{content}\\]'

# 3. Register these rules to override the default plugin output
md.add_render_rule("math_inline", render_anki_inline)
md.add_render_rule("math_block", render_anki_block)


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

    return {
        "front": no_p_markdown(front_text),
        "back": md.render(back_text),
    }
