"""Run the complete local Phase 2 setup."""

import os
from pathlib import Path
import subprocess
import sys
import sysconfig

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

from create_database import initialize_database
from seed_demo import seed
from verify_phase2 import main as verify


BACKEND = Path(__file__).resolve().parent


def run_migration() -> None:
    executable = Path(sysconfig.get_path("scripts")) / (
        "alembic.exe" if os.name == "nt" else "alembic"
    )
    alembic = str(executable) if executable.exists() else "alembic"
    result = subprocess.run(
        [alembic, "upgrade", "head"],
        cwd=BACKEND,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Alembic migration failed with exit code {result.returncode}")


def main() -> None:
    print("Initializing MySQL...")
    initialize_database()
    print("Running Alembic migration...")
    run_migration()
    print("Seeding deterministic demo data...")
    print(seed())
    print("Verifying Phase 2...")
    verify()
    print("PHASE 2 COMPLETE")


if __name__ == "__main__":
    main()
