"""
warehouse_refresh_scheduler.py
"""

from __future__ import annotations
import sys
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

REFRESH_INTERVAL_SECONDS = 300
LOADER_FILE = Path("multi_gold_to_postgres_loader.py")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("warehouse_scheduler")


def execute_loader() -> None:
    logger.info(f"Scheduler interpreter: {sys.executable}")

    result = subprocess.run(
        [sys.executable, str(LOADER_FILE)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        logger.info("Warehouse refresh completed successfully")
    else:
        logger.error(result.stderr)


def main() -> None:
    logger.info("Warehouse scheduler started")

    while True:
        start_time = datetime.now()

        execute_loader()

        elapsed = (datetime.now() - start_time).total_seconds()
        time.sleep(max(0, REFRESH_INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    main()
