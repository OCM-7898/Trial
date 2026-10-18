from __future__ import annotations

import io
import re
import tokenize

CALL_START = re.compile(r"""\bt\(\s*(?P<q>["'])(?P<key>[^"']*)(?P=q)""")


def _scan_call(source: str, start: int) -> tuple[str, int] | None:
    depth = 0
    quote = None
    index = start
    while index < len(source):
        char = source[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return source[start + 1:index], index + 1
        index += 1
    return None


class MissingKey(KeyError):
    pass


def protected_spans(source: str, is_python: bool) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    if not is_python:
        for match in re.finditer(r"(?s)\{#.*?#\}|<!--.*?-->", source):
            spans.append(match.span())
        return spans

    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))

    def at(row: int, col: int) -> int:
        return offsets[row - 1] + col

    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type in (tokenize.COMMENT, tokenize.STRING):
                spans.append((at(*token.start), at(*token.end)))
    except (tokenize.TokenError, IndentationError):
        return [(0, len(source))]
    return spans


def _inside(spans: list[tuple[int, int]], index: int) -> bool:
    return any(start <= index < end for start, end in spans)


def bake(source: str, catalogue: dict[str, str], origin: str,
         is_python: bool | None = None) -> tuple[str, int]:
    if is_python is None:
        is_python = origin.endswith(".py")
    spans = protected_spans(source, is_python)
    replaced = 0
    missing: list[str] = []
    out: list[str] = []
    position = 0

    while True:
        match = CALL_START.search(source, position)
        if match is None:
            out.append(source[position:])
            break

        if _inside(spans, match.start()):
            out.append(source[position:match.end()])
            position = match.end()
            continue

        opening = source.index("(", match.start())
        scanned = _scan_call(source, opening)
        if scanned is None:
            out.append(source[position:match.end()])
            position = match.end()
            continue

        arguments, after = scanned
        key = match.group("key")
        if key not in catalogue:
            missing.append(key)
            out.append(source[position:after])
            position = after
            continue

        remainder = arguments[len(match.group(0)) - (opening - match.start()) - 1:].strip()
        remainder = remainder.lstrip(",").strip()

        literal = _python_literal(catalogue[key])
        out.append(source[position:match.start()])
        out.append(f"{literal}.format({remainder})" if remainder else literal)
        position = after
        replaced += 1

    result = "".join(out)
    if missing:
        raise MissingKey(
            f"{origin}: keys not in the catalogue: {sorted(set(missing))}. "
            "The catalogues are asserted equal by tests/test_catalogue_parity.py, "
            "so this means a call site references a key nobody added."
        )
    return result, replaced


def _python_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", "\\n").replace("\r", "").replace("\t", "\\t")
    return f'"{escaped}"'


def remaining_calls(source: str, is_python: bool = True) -> list[str]:
    spans = protected_spans(source, is_python)
    found = []
    for match in CALL_START.finditer(source):
        if not _inside(spans, match.start()):
            line = source.count("\n", 0, match.start()) + 1
            found.append(f"line {line}: {match.group(0)}")
    return found
