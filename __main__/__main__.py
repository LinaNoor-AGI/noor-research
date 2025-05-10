"""
__main__.py · v1.0.0

Entry‑point shim for the Noor triad package.

Invoked via:

    python -m noor     # assuming package name 'noor'

It simply defers to `noor.orchestrator.main()`, forwarding CLI args.
"""
from __future__ import annotations

import sys

from noor.orchestrator import main as _orchestrator_main

if __name__ == "__main__":
    _orchestrator_main(sys.argv[1:])

# END_OF_FILE
