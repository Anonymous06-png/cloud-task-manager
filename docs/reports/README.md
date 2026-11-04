# Reports — Cloud Task Manager

The files in this folder are **historical engineering and test evidence**, not a claim that the present production environment has passed verification. Read the date, environment and PASS/FAIL/NOT RUN fields in each report.

For the official assessment requirements, see [the assignment](../Project-Cloud-Computing.pdf) and [the requirements tracker](../requirements.md).

## Key implementation and verification reports

| Area | Reports |
| --- | --- |
| Foundation | [Foundation verification](step-02b-foundation-verification.md), [authentication](step-03-authentication.md) |
| Local PostgreSQL | [Isolated PostgreSQL runtime](step-04i-isolated-postgresql-runtime.md), [safe local runtime](step-04i-postgresql-safe-local-runtime.md), [PostgreSQL diagnostic](step-04i-extractor-diagnostics.md), [migration verification](step-04j-b-migration-verification.md) |
| Local app and backend | [Website preview](step-04j-c-local-website-preview.md), [backend tests](step-04k-b-backend-test-results.md), [backend verification](step-04k-c-backend-verification.md), [launcher fix](step-04k-c-launcher-import-fix.md), [isolation preflight](step-04l-agent-pgpassfile-preflight.md), [PGPASSFILE recovery](step-04l-b-pgpassfile-recovery.md) |
| Frontend | [Browser functional QA](step-05b-browser-functional-qa.md), [bilingual UI](step-05c-bilingual-ui.md), [Figma design](step-05d-b-figma-design.md) |
| GitHub | [GitHub publication](step-05f-github-publication.md) |

**Pending branches (not merged into main at the time of this indexing):** [Task 05E UI PR #1](https://github.com/Anonymous06-png/cloud-task-manager/pull/1) includes its own report and records 55 Django tests (51 passing, 4 text assertions failing). [Documentation PR #2](https://github.com/Anonymous06-png/cloud-task-manager/pull/2) includes the separate documentation-hygiene report.

## Older task logs

The 23 incremental or superseded reports were preserved byte-for-byte in [../archive/reports/](../archive/reports/README.md). These include environment troubleshooting, old UI completion claims and initial audits; **do not use them as the current status**.

New agent tasks should continue to write a **new report in this folder**, not overwrite a past report.
