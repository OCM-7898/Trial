import ast
import re

from conftest import python_sources, template_code, templates

TEMPLATE_CALL = re.compile(r"\bt\(\s*([^)]*?)\s*[,)]")


def test_python_t_calls_use_literal_keys():
    offenders = []
    for path in python_sources():
        tree = ast.parse(path.read_text("utf-8"), str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
            if name != "t" or not node.args:
                continue
            if not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                offenders.append(f"{path}:{node.lineno}: non-literal translation key")
    assert not offenders, "\n".join(offenders)


def test_template_t_calls_use_literal_keys():
    offenders = []
    for path in templates():
        for lineno, line in enumerate(template_code(path).splitlines(), 1):
            for arg in TEMPLATE_CALL.findall(line):
                arg = arg.strip()
                if not (arg.startswith(('"', "'")) and arg.endswith(('"', "'"))):
                    offenders.append(f"{path.name}:{lineno}: t({arg}) is not a literal key")
    assert not offenders, (
        "templates must not compute translation keys; resolve them in the view:\n"
        + "\n".join(offenders)
    )
