# Task 06B continuation — UTF8 repair authentication preflight

Date: 2026-11-05. Repository: `C:\ProjectCloud\cloud-task-manager`.

## Result: BLOCKED — target database authentication

Resumed from `docs/reports/step-06b-task-create-post500-root-cause.md`; did not restart the root-cause investigation. The established cause remains WIN1252 storage rejecting Vietnamese/emoji input (SQLSTATE 22P05).

The user created both additive databases and authorized continuation of data-preserving restore, validation, tests and eventual identified-runtime switch. **Both target catalog identities/encodings/owners were independently confirmed.** However, connecting as `cloudtask_app` to `cloudtask_dev_utf8_06b` returned **`no password supplied`** using the configured external PGPASSFILE. Following the user's explicit stop-on-authentication-blocker instruction, work stopped before restore, database preparation or runtime switch. **Not FIXED.**

No password contents were displayed or extracted, no existing password entry was copied, no wildcard password entry was added, and no alternate credential source/role was searched or tried. No authentication/security setting or role privilege was changed.

## Preserved state and scope

Initial actual Git status:

```text
## main...origin/main
 M tasks/test_task_crud.py
 M tasks/tests.py
?? docs/reports/step-06-full-local-stabilization.md
?? docs/reports/step-06b-task-create-post500-root-cause.md
```

All existing changes were preserved. No tracked source or prior report was edited in this continuation. Only this new report was added to the workspace; a private preflight script/log was written outside the repository. No Plan Mode, subagents, Git state-changing operations, `.env` writes, dependency changes, database resets/drops, cloud/Docker/WSL operations or application logic changes.

Prior 06B report SHA-256 at continuation start:

`f891e72eeafb85c8a18dc9ec31a641f0e536687fc505d9e383c02dd0477b9f00`

## Actual preflight evidence

External authentication file used by the diagnostic process:

`%LOCALAPPDATA%\CloudTaskManager\pgpass.conf`

The script sets PGPASSFILE to that established path and uses `psycopg2.connect` with explicit database/user/host/port and a five-second timeout. It never reads or prints password-file contents. Identity SQL is constant or parameter-bound; no external input is interpolated into SQL.

### Source database — authenticated identity PASS

```text
current_database: cloudtask_dev
current_user: cloudtask_app
server_address: 127.0.0.1
server_port: 55432
encoding: WIN1252
owner: cloudtask_app
collation/ctype: English_United States.1252
source tasks: count=9, min(id)=1, max(id)=11
```

The original database still authenticates successfully with the existing configuration. This confirms the source is accessible, not that the target authentication is configured. Task count/ID range matches the final previous 06B evidence; no claim is made that other tables or individual values have not changed since the backup.

### Target catalog identity/owner/encoding — PASS

Queried `pg_database` through the authenticated source connection using parameter-bound database names:

| Database | Encoding | Owner |
| --- | --- | --- |
| `cloudtask_dev_utf8_06b` | **UTF8** | **cloudtask_app** |
| `cloudtask_test_utf8_06b` | **UTF8** | **cloudtask_app** |

### Direct target authentication — BLOCKED

```text
VERIFY_DATABASE cloudtask_dev_utf8_06b
BLOCKED_AUTH cloudtask_dev_utf8_06b no password supplied
```

The script exits **2** on the first authentication blocker. It does not retry, fall back to an admin role, or continue to the test target.

- Direct UTF8 dev identity and target emptiness: **BLOCKED / NOT VERIFIED**.
- Direct UTF8 test connection, identity and emptiness: **NOT RUN**, stopped at first blocker.
- Target catalog existence, UTF8 encoding and owner are established; they do not prove direct app-role authentication.
- `no password supplied` is not `password authentication failed`: libpq did not find usable password authentication for the exact new database target. The old narrowly scoped entries do not automatically cover the new names. The file contents were not inspected, so no claim is made about their precise current entries.

## Backup integrity and data-preservation boundary

Existing private dump:

`C:\Users\Ky\AppData\Local\Temp\ctm-task06b-20261105\cloudtask-dev-before-utf8.dump`

Expected and independently recomputed SHA-256:

`31ef47dc02516f441184587fd277ee4a65e96af25407e24d4751c70f99e51675`

**Hash PASS**, both shell sha256sum and Python assertion. The previous report records pg_dump exit 0 and pg_restore archive-index exit 0. This continuation did not redo archive restoration or infer restored-data integrity from a hash alone.

**No restore has occurred.** To preserve writes after the earlier backup, do not use that snapshot as the final cutover state without reconciliation. After authentication is fixed:

1. Verify both targets directly, ownership/encoding and whether either contains objects. Stop on any unexpected target data; never clean/drop it to force restoration.
2. Validate a fresh snapshot/restore before cutover as authorized. Establish a controlled final write boundary for the identified app before the final snapshot/reconciliation; inventory other source writers as applicable.
3. Preserve all later source writes through a new uniquely named final backup or explicitly verified reconciliation. No earlier dump may overwrite current data silently.
4. Compare complete table counts, exact primary keys/critical values/owners and sequence states against the final source snapshot, not just task count.
5. Run the previously red Unicode regression and affected suites on the isolated UTF8 test DB before the normal-runtime switch.

No source/target table writes, migrations, sequence changes or destructive operations were performed by this continuation. No backup or database was overwritten.

## Runtime and rollback status

Reidentified current runtime, not assumed from stale PID context:

- Listener **127.0.0.1:8000**, PID **2472**.
- Owner **`LAPTOP-214UR8HL\Ky`**.
- Command: system Python `manage.py runserver 127.0.0.1:8000 --noreload`.
- Parent PID **13552**.
- PostgreSQL listener PID **18392**, 127.0.0.1/::1:55432.

**No process stopped or restarted. No configuration switch.** Port 8000 remains on its existing runtime. Original WIN1252 databases remain preserved for rollback; no rollback is needed because no cutover occurred. User-created UTF8 databases were not modified. Corrected runtime HTTP/browser acceptance remains unavailable until authentication/restore/testing is completed.

The persistent normal launcher still points at the original database as documented previously; this task did not edit it. A later authorized switch must use the validated process-local configuration and document how to start that repaired runtime safely without silently reverting to WIN1252.

## Commands and actual exit codes

All shell work from repository root; existing `.venv/Scripts/python.exe`; no package installation.

| Command/action | Exit | Result |
| --- | ---: | --- |
| `git status --short --branch` | 0 | Existing Task 06/06B changes recorded, branch main unchanged |
| `sha256sum C:/Users/Ky/AppData/Local/Temp/ctm-task06b-20261105/cloudtask-dev-before-utf8.dump docs/reports/step-06b-task-create-post500-root-cause.md` | 0 | Both hashes above recorded |
| PowerShell `Get-NetTCPConnection -State Listen` filtered to ports 8000/55432; `Get-CimInstance Win32_Process`; `Invoke-CimMethod ... GetOwner` | 0 | Existing listener/owner/process verified; read-only |
| `PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -I -B C:/Users/Ky/AppData/Local/Temp/ctm-task06b-continuation-20261105/preflight.py > C:/Users/Ky/AppData/Local/Temp/ctm-task06b-continuation-20261105/preflight.log 2>&1` | **2** | Backup assertion PASS; source identity PASS; both target catalog UTF8/owners PASS; first direct target auth BLOCKED |

Private script/log directory:

`C:\Users\Ky\AppData\Local\Temp\ctm-task06b-continuation-20261105`

The script only logs safe identity/count fields and a categorized authentication error; no raw connection exception/credentials/SQL values/user content/session tokens are dumped. The prior backup contains sensitive user/password-hash/session data and remains outside Git; do not publish it.

Closing checks: `git diff --check`, new-report whitespace, unchanged prior-report hash and final Git status are run after creating this report. System checks/tests are explicitly not claimed from those static checks.

## Verification results / counts

| Required operation | Result |
| --- | --- |
| Backup hash integrity | **PASS** |
| Source authenticated identity | **PASS** |
| Both target catalog identities/owners/UTF8 | **PASS** |
| Direct target authentication | **BLOCKED** on first target |
| Fresh final source snapshot | **NOT RUN**, stop-on-authentication-blocker |
| Restore into UTF8 dev | **NOT RUN** |
| Full source/target table, PK, value, owner, sequence equivalence | **NOT RUN** |
| Prepare isolated UTF8 test DB | **NOT RUN** |
| Unicode regression / affected PostgreSQL tests | **0 tests executed in this continuation**, BLOCKED |
| Django system check | **NOT RUN in this continuation**, no runtime/source fix applied |
| Runtime switch/restart | **NOT RUN** |
| Corrected real HTTP/browser Vietnamese/emoji create/edit/filter/delete/invalid/persistence | **NOT RUN**, BLOCKED |
| Original WIN1252 rollback databases | **PRESERVED**, no cutover |

The historical red test from 06B remains known evidence; no new success/failure count is substituted for it. Full repair is still incomplete and no FIXED/PASS claim is made.

## Required next action

Configure application authentication for the **two exact new database names** in the existing private PGPASSFILE (or another explicitly approved private authentication mechanism), without changing PostgreSQL security or granting extra privileges. Required pgpass scopes:

```text
host=127.0.0.1 port=55432 database=cloudtask_dev_utf8_06b user=cloudtask_app
host=127.0.0.1 port=55432 database=cloudtask_test_utf8_06b user=cloudtask_app
```

Use the existing cloudtask_app password privately; do not paste it into chat, command history, the repository, or this report. Keep prior entries intact, avoid wildcards, retain restricted file access, UTF8 without BOM, and proper pgpass escaping. Database creation as admin did not automatically provision the app's password-file entries for those new names.

Once configured, noninteractive verification can use the existing local psql binary with `-X -w -h 127.0.0.1 -p 55432 -U cloudtask_app -d <exact new name>` and identity-only SELECTs. Never add a password to the command line. Stop on any authentication or identity error. Resume from this preflight; do not restart the encoding investigation.

## Expected final Git status

```text
## main...origin/main
 M tasks/test_task_crud.py
 M tasks/tests.py
?? docs/reports/step-06-full-local-stabilization.md
?? docs/reports/step-06b-task-create-post500-root-cause.md
?? docs/reports/step-06b-utf8-repair-continuation.md
```

Only the final report is new repository content in this continuation. Prior source changes and original 06B report preserved; no staging, commit, publication, reset or clean.
