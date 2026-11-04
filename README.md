# Cloud Task Manager

Web application for personal task management, built for a Cloud Computing course project.

**Status (2026-11-04):** Django application development is in progress. A public cloud deployment and grading-ready URL have **not been verified**. The updated Figma-based UI is proposed in [PR #1](https://github.com/Anonymous06-png/cloud-task-manager/pull/1), not yet part of the main branch.

## Project and architecture

- Application: Django 5.2, server-rendered Django Templates, HTML/CSS and minimal JavaScript.
- Authentication: Django sessions, server-side ownership checks and CSRF protection.
- Database: PostgreSQL 16.
- App server: Gunicorn; containerization: Docker and Docker Compose.
- Cloud target: deployment design is pending final infrastructure verification. Prior planning included Azure Ubuntu VM/Caddy; a VPS NAT/Cloudflare Tunnel path was also evaluated. Neither should be described as a successfully deployed Django production system without runtime evidence.

The task model and application include registration/login, task CRUD, status filtering and a health endpoint. Browser and database evidence for earlier local functionality is recorded in docs/reports. UI work in PR #1 is **not** on main until merged.

## Local run with Docker Compose

Prerequisites: Docker Engine with Docker Compose, Git and a Docker-supported host.

1. Copy .env.example to .env (PowerShell: Copy-Item .env.example .env).
2. Replace the placeholder SECRET_KEY and POSTGRES_PASSWORD with strong values. **Never commit .env.**
3. Run:

~~~sh
docker compose up --build -d
docker compose ps
~~~

The app is available at http://127.0.0.1:8080/ and its health endpoint at http://127.0.0.1:8080/health/. The database stays on the internal Docker network and uses a named volume.

To inspect logs or run checks:

~~~sh
docker compose logs --tail=100 app
docker compose exec app python manage.py check
docker compose exec app python manage.py test
~~~

For a non-destructive stop, use docker compose stop. **Do not use down -v or prune to clean up**: those operations can remove persistent data. This section documents intended Compose use, not a claim that every host has been verified.

A separately configured Windows Python + isolated PostgreSQL development instance was also used for local tests. Its host settings are machine-specific and not a portable deployment method.

## Cloud deployment and assessment

A release is not complete until the team has demonstrated:

1. A public URL and repeatable deployment from Docker.
2. Working authentication and task CRUD with PostgreSQL persistence after an app restart.
3. Successful /health/, graceful handling of invalid input and inspectable request/error logs.
4. At least one monitoring metric, budget/cost monitoring and a monthly cost estimate.
5. Least-privilege networking, protected secrets and a documented cleanup procedure.
6. A demo account with sample data and a verified test report for T1–T7.

**Status:** Cloud-specific T1–T7, production metrics, exact monthly cost and public Django deployment are **NOT RUN / not yet evidenced** in the current repository. Do not present local smoke checks as deployed-cloud verification.

## Submission checklist

The official requirements are in [docs/Project-Cloud-Computing.pdf](docs/Project-Cloud-Computing.pdf). Deliverables include the Git URL, live public URL, a 10–20 page PDF report, slides, a 5–7 minute demo video and the member contribution table. The README, architecture diagram and test evidence must describe the deployment actually used for grading.

Team member names, final infrastructure details, deployment evidence and cost figures must be supplied and verified before submission.

## Repository guide

| Path | Purpose |
| --- | --- |
| config/, tasks/, templates/, static/, locale/ | Active Django source and assets |
| Dockerfile, docker-compose.yml, requirements.txt, .env.example | Runtime/deployment definition |
| docs/Project-Cloud-Computing.pdf | Official assignment |
| docs/requirements.md | Requirement-to-evidence tracking (not authoritative over the PDF) |
| docs/design/ | Historical UI prototype and Figma design reference; **not** the running application |
| docs/reports/ | Historical agent/test evidence. Older reports may describe outdated states and are not a substitute for current checks |
| docs/archive/legacy-node/ | Inactive Node.js reference kept for historical traceability |
| backend/ | Duplicate **inactive** legacy Node.js source, not Django's active backend |
| tools/ | Historical local test helpers |

The project does not use the legacy Node.js application. Do not remove historical evidence, legacy archives or local data during routine cleanup without explicit approval.

## Security

Never commit real .env files, passwords, access tokens, SSH private keys or credential-bearing database URLs. Use environment variables or a secret manager. Review the public repository and reports before sharing them with third parties.

## Known pending items

- PR #1 UI integration is awaiting review/merge; its report documents 55 Django tests: 51 passed and four text/language assertion failures. These are **reported cloud-branch results**, not a test run performed by this README update.
- Team members, architecture illustration, seed/demo instructions, production deployment, monitoring/cost evidence and final T1–T7 results still need accurate, current documentation.
