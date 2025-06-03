"""
run_noor.py · v1.0.0

Unified CLI launcher for the Noor Triad system.

Usage:
    python run_noor.py --tick-rate 50 --metrics-port 9000

Equivalent to:
    python -m noor --tick-rate 50 --metrics-port 9000

This script provides a simple runtime entrypoint for local testing or
integration within IDEs and Windows shells.
"""

from __future__ import annotations
import sys

try:
    from noor.orchestrator import main as _orchestrator_main
except ImportError as e:
    print("❌ Could not import 'noor.orchestrator'. Check your install.")
    raise e

if __name__ == "__main__":
    print("🔧 Launching Noor Triad...")
    _orchestrator_main(sys.argv[1:])

# End of File
