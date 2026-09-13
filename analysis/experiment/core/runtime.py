"""ReviewGate — handler-body I/O policy (single source of truth).

Mode B inserts a fixed artificial I/O latency to model external/business work;
Mode A runs the handler body with no artificial cost. The same function is
called at the top of every rendered handler in every strategy.
"""

from __future__ import annotations

import os
import time


def io_sleep() -> None:
    if os.environ.get("REVIEWGATE_MODE") == "B":
        time.sleep(float(os.environ.get("REVIEWGATE_IO_MS", "5")) / 1000.0)