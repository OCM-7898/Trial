import subprocess
import sys

import pytest

from conftest import ROOT


@pytest.mark.slow
def test_verify_parity_passes():
    result = subprocess.run(
        [sys.executable, "verify_parity.py"], cwd=ROOT,
        capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        "verify_parity.py failed:\n" + result.stdout + result.stderr
    )


@pytest.mark.slow
def test_parity_covers_every_built_route():
    import re

    from app import create_app

    listing = (ROOT / "spec" / "parity_routes.txt").read_text("utf-8")
    listed = {line.split("?", 1)[0].strip()
              for line in listing.splitlines()
              if line.strip() and not line.startswith("#")}

    skip = {"/reset", "/reset/status"}
    missing = []
    for rule in create_app("en").url_map.iter_rules():
        if rule.endpoint == "static":
            continue
        template = str(rule)
        if template in skip or ".pdf" in template:
            continue
        pattern = re.sub(r"<[^>]+>", "[^/]+", template)
        if not any(re.fullmatch(pattern, candidate) for candidate in listed):
            missing.append(template)

    assert not missing, (
        "routes with no entry in spec/parity_routes.txt: " + str(sorted(missing))
        + "\nregenerate with: python tools/make_parity_routes.py"
    )
