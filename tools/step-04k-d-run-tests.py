"""Visible-terminal runner for the isolated 04K Django suites."""

import getpass
import os
import subprocess
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
LAUNCHER = os.path.join(ROOT, "tools", "step-04k-c-test-launcher.py")
SUITES = ("tasks.test_authentication", "tasks.test_task_crud")


def main():
    password = getpass.getpass("cloudtask_app password (not echoed): ")
    environment = os.environ.copy()
    environment["DJANGO_SETTINGS_MODULE"] = "config.settings"
    environment["SECRET_KEY"] = "local-04k-test-only"
    environment["DATABASE_URL"] = (
        "postgresql://cloudtask_app:"
        + quote(password, safe="")
        + "@127.0.0.1:55432/cloudtask_test_04k"
    )
    environment["CLOUDTASK_TEST_KEEPDB"] = "1"
    del password

    for suite in SUITES:
        print(f"START_SUITE={suite}", flush=True)
        completed = subprocess.run(
            [PYTHON, "-I", "-B", LAUNCHER, suite],
            cwd=ROOT,
            env=environment,
            check=False,
        )
        print(f"SUITE_EXIT={suite}:{completed.returncode}", flush=True)
        if completed.returncode != 0:
            print("STOPPED_AFTER_FAILURE=1", flush=True)
            return completed.returncode
    print("ALL_SUITES_COMPLETED=1", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
