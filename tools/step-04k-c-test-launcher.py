"""Run one approved Django test suite against the isolated 04K database."""

import os
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

import django
from django.conf import settings
from django.db import connections
from django.test.runner import DiscoverRunner

EXPECTED_DATABASE = "cloudtask_test_04k"
EXPECTED_HOST = "127.0.0.1"
EXPECTED_PORT = 55432
ALLOWED_LABELS = {
    "tasks.test_authentication",
    "tasks.test_task_crud",
}


def fail(message):
    print(f"BLOCKED: {message}", file=sys.stderr)
    raise SystemExit(2)


def verify_environment():
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        fail("DATABASE_URL must be set in this process environment")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    database = settings.DATABASES["default"]
    if database.get("ENGINE") != "django.db.backends.postgresql":
        fail("DATABASE_URL did not select PostgreSQL")
    if database.get("HOST") != EXPECTED_HOST:
        fail("database host is not the approved loopback host")
    if int(database.get("PORT") or 0) != EXPECTED_PORT:
        fail("database port is not the approved isolated port")
    if database.get("NAME") != EXPECTED_DATABASE:
        fail("DATABASE_URL database is not cloudtask_test_04k")

    database.setdefault("TEST", {})["NAME"] = EXPECTED_DATABASE
    connection = connections["default"]
    connection.settings_dict.setdefault("TEST", {})["NAME"] = EXPECTED_DATABASE
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT current_database(), current_user, "
            "host(inet_server_addr()), inet_server_port(), "
            "pg_get_userbyid(datdba) "
            "FROM pg_database WHERE datname = current_database()"
        )
        row = cursor.fetchone()
    if row is None:
        fail("database identity query returned no row")
    current_database, current_user, server_address, server_port, owner = row
    if current_database != EXPECTED_DATABASE:
        fail("authenticated connection is not cloudtask_test_04k")
    if current_database == "cloudtask_dev":
        fail("refusing to connect to cloudtask_dev")
    if server_address != EXPECTED_HOST or server_port != EXPECTED_PORT:
        fail("authenticated connection is not the approved isolated PostgreSQL")
    if owner != "cloudtask_app" or current_user != "cloudtask_app":
        fail("test database is not owned and accessed by cloudtask_app")
    print(
        "ISOLATION=PASS database=cloudtask_test_04k "
        "user=cloudtask_app host=127.0.0.1 port=55432"
    )


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ALLOWED_LABELS:
        print(
            "usage: step-04k-c-test-launcher.py "
            "tasks.test_authentication|tasks.test_task_crud",
            file=sys.stderr,
        )
        return 2
    verify_environment()
    if os.environ.get("CLOUDTASK_TEST_KEEPDB") != "1":
        fail("set CLOUDTASK_TEST_KEEPDB=1 only after manual reuse verification")
    runner = DiscoverRunner(verbosity=2, keepdb=True)
    failures = runner.run_tests([sys.argv[1]])
    return int(failures)


if __name__ == "__main__":
    raise SystemExit(main())
