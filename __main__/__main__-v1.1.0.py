"""
__main__.py · v1.1.0

Zero-footprint entry-point for the Noor triad package.

Typical invocation:
    python -m noor  --tick-rate 50 --metrics-port 9000

This simply defers to `noor.orchestrator.main()` with all args forwarded.
"""

from __future__ import annotations
import sys

try:
    from noor.orchestrator import main as _orchestrator_main
except ImportError as e:
    print("🚨 Failed to import orchestrator. Ensure Noor is installed correctly.")
    raise e

if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print("🔧 Noor Triad Launcher\n")
        print("Example:")
        print("  python -m noor --tick-rate 50 --metrics-port 9000\n")
        print("All flags are passed to `orchestrator.py`. Run with --log-level DEBUG for trace output.\n")
    _orchestrator_main(sys.argv[1:])

# End of File
