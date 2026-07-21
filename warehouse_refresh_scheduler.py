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

SILVER_FILE = Path("spark/silver_transform.py")
GOLD_FILE = Path("spark/gold_aggregations.py")
LOADER_FILE = Path("multi_gold_to_postgres_loader.py")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("warehouse_scheduler")


def run_stage(script_path: Path, stage_name: str) -> bool:
    logger.info(f"Running {stage_name} ({script_path}) ...")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        logger.info(f"{stage_name} completed successfully")
        return True
    else:
        logger.error(f"{stage_name} FAILED:\n{result.stderr}")
        return False


def execute_refresh_cycle() -> None:
    logger.info(f"Scheduler interpreter: {sys.executable}")

    if not run_stage(SILVER_FILE, "Silver transform"):
        logger.warning("Skipping Gold + Load this cycle due to Silver failure.")
        return

    if not run_stage(GOLD_FILE, "Gold aggregations"):
        logger.warning("Skipping Load this cycle due to Gold failure.")
        return

    run_stage(LOADER_FILE, "Neon load (multi-loader)")


def main() -> None:
    logger.info("Warehouse scheduler started")

    while True:
        start_time = datetime.now()

        execute_refresh_cycle()

        elapsed = (datetime.now() - start_time).total_seconds()
        time.sleep(max(0, REFRESH_INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    main()