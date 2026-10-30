"""SACL V1 CLI Package Entrypoint.

Allows invocation via python -m sacl.cli.
"""

from __future__ import annotations

import sys

from sacl.cli.main import main

if __name__ == "__main__":
    sys.exit(main())
