# Cloud Task Manager — Agent project contract

## Active application

- Django 5.2 with server-rendered templates and minimal vanilla JavaScript.
- PostgreSQL 16, Django sessions/auth, Docker / Docker Compose, Gunicorn.
- Active Django project: config/; application: tasks/; UI: templates/, static/, locale/.
- Legacy Node.js in backend/ and docs/archive/legacy-node/ is **inactive**.
- Cloud deployment configuration must follow the team's latest approved target; do not claim an Azure/VPS production deployment without current evidence.

## Priority and source of truth

1. docs/Project-Cloud-Computing.pdf for grading requirements.
2. Current source and actual commands for runtime behavior.
3. Latest handoff/task reports for decisions and past evidence. Old reports can be superseded.
4. Explicit user decisions for future changes.

## Scope and safety

- Work on one small assigned task only; reuse existing implementation.
- Do not change the framework or database architecture, install unrelated tools, update dependencies in bulk, or touch WebIOT.
- No destructive Git operations, staging, commits, pushes, merges, database/volume removal or paid cloud resources without explicit user authorization.
- Never overwrite a real .env or display/store secrets.
- Keep historical archive and previous reports unless specifically authorized to reorganize them.

## Verification and reporting

- PASS means executed successfully; FAIL means executed and failed.
- FIXED IN SOURCE means changed without runtime verification.
- NOT RUN and BLOCKED must be stated explicitly.
- Select only tests relevant to the assigned task; do not claim a Docker build or UI browser QA from code inspection.
- An agent editing the repository must create a **new** sanitized Markdown report under docs/reports/, including scope, files changed, commands/results/exit codes when applicable, actual test counts, blockers, risks, Git status and next permitted step.
- Keep PR changes reviewable; do not automatically merge.
