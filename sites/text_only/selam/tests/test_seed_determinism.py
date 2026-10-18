import hashlib
import os
import subprocess
import sys

import pytest

from conftest import ROOT

DB = ROOT / "data" / "seed.db"


def _seed_with_hash_seed(value: str) -> str:
    env = dict(os.environ, PYTHONHASHSEED=value)
    result = subprocess.run(
        [sys.executable, "seed.py"], cwd=ROOT, env=env,
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    return hashlib.sha256(DB.read_bytes()).hexdigest()


@pytest.mark.slow
def test_seed_is_byte_identical_across_hash_seeds():
    digests = {seed: _seed_with_hash_seed(seed) for seed in ("0", "1", "424242")}
    assert len(set(digests.values())) == 1, (
        "seed.db is not reproducible; digests by PYTHONHASHSEED: " + repr(digests)
    )
