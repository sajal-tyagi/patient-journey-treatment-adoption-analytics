"""
run_project.py
--------------
One-command pipeline runner for the Patient Journey & Treatment Adoption Analytics project.

Usage:
    python src/run_project.py

This script runs the full pipeline:
  1. generate_data.py  — creates data/patient_data.csv
  2. clean_data.py     — creates data/patient_data_clean.csv
  3. analyze.py        — creates all results, charts, and reports
"""

import subprocess
import sys
import os
import time


def run(script: str) -> None:
    print(f"\n{'='*65}")
    print(f"  Running: {script}")
    print(f"{'='*65}")
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False,
        text=True,
    )
    if result.returncode != 0:
        print(f"\n❌  ERROR: {script} failed with exit code {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    # Ensure we are always running from the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    start = time.time()
    print("\n🚀  Patient Journey & Treatment Adoption Analytics — Full Pipeline")
    print("    Running from:", os.getcwd())

    run("src/generate_data.py")
    run("src/clean_data.py")
    run("src/analyze.py")

    elapsed = time.time() - start
    print(f"\n✅  Full pipeline completed in {elapsed:.1f} seconds.")
    print("\nOutputs:")
    print("  data/patient_data.csv")
    print("  data/patient_data_clean.csv")
    print("  results/  — CSV result tables")
    print("  outputs/  — PNG charts")
    print("  reports/  — Markdown reports")
