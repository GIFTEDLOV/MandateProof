"""Prepare the GenVM bundle expected by genlayer-test 0.29.2.

The published harness still requests the historical ``genvm-universal`` asset,
while current GenVM releases publish the same runner bundle as
``genvm-runners-all``.  Downloading the exact pinned release into the harness
cache keeps CI reproducible without changing the contract or patching the
installed package.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import urllib.request
from pathlib import Path


VERSION = os.environ.get("MANDATEPROOF_GENVM_VERSION", "v0.3.0-rc7")
CACHE = Path.home() / ".cache" / "gltest-direct"
DEST = CACHE / f"genvm-universal-{VERSION}.tar.xz"
URL = (
    "https://github.com/genlayerlabs/genvm/releases/download/"
    f"{VERSION}/genvm-runners-all.tar.xz"
)


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    if DEST.is_file():
        print(f"GENVM_BUNDLE_CACHE=HIT {DEST}")
        return 0

    print(f"GENVM_BUNDLE_DOWNLOAD={URL}")
    request = urllib.request.Request(URL, headers={"User-Agent": "MandateProof-CI"})
    with urllib.request.urlopen(request, timeout=300) as response:
        with tempfile.NamedTemporaryFile(delete=False, dir=CACHE) as temporary:
            temporary_path = Path(temporary.name)
            shutil.copyfileobj(response, temporary)
    temporary_path.replace(DEST)
    print(f"GENVM_BUNDLE_CACHE=READY {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
