from __future__ import annotations

import io
import re
import tokenize


def strip_python(source: str) -> str:
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError):
        return source

    drop: list[tuple[int, int, int, int]] = []
    previous_type = tokenize.INDENT
    for token in tokens:
        if token.type == tokenize.COMMENT:
            drop.append((*token.start, *token.end))
        elif token.type == tokenize.STRING and previous_type in (
            tokenize.INDENT, tokenize.NEWLINE, tokenize.NL, tokenize.DEDENT,
            tokenize.ENCODING,
        ):
            drop.append((*token.start, *token.end))
        if token.type not in (tokenize.NL, tokenize.COMMENT):
            previous_type = token.type

    lines = source.splitlines(keepends=True)
    for start_row, start_col, end_row, end_col in reversed(drop):
        if start_row == end_row:
            line = lines[start_row - 1]
            replacement = line[:start_col] + line[end_col:]
            lines[start_row - 1] = replacement if replacement.strip() else ""
        else:
            head = lines[start_row - 1][:start_col]
            tail = lines[end_row - 1][end_col:]
            merged = head + tail
            lines[start_row - 1:end_row] = [merged if merged.strip() else ""]

    text = "".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.lstrip("\n")


def strip_css(source: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"(?s)/\*.*?\*/", "", source)).lstrip()


def strip_js(source: str) -> str:
    text = re.sub(r"(?s)/\*.*?\*/", "", source)
    text = re.sub(r"(?m)^\s*//.*$\n?", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).lstrip()


def strip_markup(source: str) -> str:
    text = re.sub(r"(?s)<!--.*?-->", "", source)
    text = re.sub(r"(?s)\{#.*?#\}", "", text)
    return re.sub(r"\n{3,}", "\n\n", text)


STRIPPERS = {
    ".py": strip_python, ".css": strip_css, ".js": strip_js,
    ".html": strip_markup, ".svg": strip_markup,
}
