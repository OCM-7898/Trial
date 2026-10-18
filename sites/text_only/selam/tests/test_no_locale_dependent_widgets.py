import re

from conftest import template_code, templates

BANNED = re.compile(r"""type\s*=\s*["'](date|datetime-local|time|month|week)["']""", re.I)


def test_no_native_date_widgets():
    offenders = []
    for path in templates():
        for lineno, line in enumerate(template_code(path).splitlines(), 1):
            m = BANNED.search(line)
            if m:
                offenders.append(f"{path.name}:{lineno}: type={m.group(1)}")
    assert not offenders, (
        "use the date_field macro instead of a native locale-dependent widget:\n"
        + "\n".join(offenders)
    )
