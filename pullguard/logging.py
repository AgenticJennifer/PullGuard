from __future__ import annotations
import logging
import os
import sys
from typing import Literal


def configure_logging(mode: Literal["cli", "server"] = "server") -> None:
    level = os.environ.get("PULLGUARD_LOG_LEVEL", "INFO").upper()
    root = logging.getLogger("pullguard")
    root.setLevel(getattr(logging, level, logging.INFO))

    if mode == "server":
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter("%(levelname)s [%(name)s] %(message)s")

    handler.setFormatter(formatter)
    root.handlers.clear()
    root.addHandler(handler)
