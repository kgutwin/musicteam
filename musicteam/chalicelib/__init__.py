import functools
import os
import subprocess
from datetime import datetime
from datetime import timezone


@functools.cache
def _version() -> str:
    if "GIT_REVISION" in os.environ:
        return os.environ["GIT_REVISION"]

    # fallback: try to read it from git
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, encoding="utf8"
    )
    return result.stdout.strip()


@functools.cache
def _deployed_at() -> str:
    if "DEPLOYED_AT" in os.environ:
        return os.environ["DEPLOYED_AT"]

    return datetime.now(timezone.utc).isoformat()
