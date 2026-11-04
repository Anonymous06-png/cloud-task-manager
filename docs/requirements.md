# Cloud Task Manager — Requirements and evidence

**Source of authority:** [Project-Cloud-Computing.pdf](Project-Cloud-Computing.pdf), six pages. This document is an implementation tracker, not a replacement for the assignment.

**Snapshot:** 2026-11-04. "Present in source" and historical agent-reported passes do not imply a verified live cloud deployment.

## Mandatory application scope

| Requirement from PDF | Source / evidence status |
| --- | --- |
| Account registration and login | Implemented in Django, covered by earlier local browser/test reports |
| Create, view, edit, delete tasks | Implemented; earlier local CRUD/browser reports available |
| Task name, description, due date and status | Present in Django forms/model |
| Filter pending vs completed | Implemented; PR #1 also adds task-list search |
| Database persistence | PostgreSQL runtime and restart behavior reported in local tests; **cloud persistence not verified** |
| Server-rendered web UI | Present; refreshed UI on PR #1, not yet merged into main |
| Health endpoint | /health/ exists; public-cloud check not verified |
| Demo account and sample data | Final grading-ready demo data not verified |

Django, PostgreSQL and Docker Compose are project choices. The PDF allows alternative stacks but the team has selected the existing Django implementation.

## Cloud, security and documentation requirements

- Dockerfile and reproducible image on a second machine.
- Public URL at grading time (or reliable redeployment when turned off).
- Compute, database, application logs and at least one metric/monitoring view.
- Environment-variable/secret management; no real credentials in Git.
- Minimal exposed ports, appropriate permissions and MFA where applicable.
- Budget monitoring/alert or equivalent cost evidence, one-month estimate with assumptions, resource cleanup steps.
- Documentation of architecture, deployment, verification, team assignments and contribution percentages.

**Deployment decision:** Azure Ubuntu VM/Caddy was previously planned. A later handoff explored VPS NAT + Cloudflare Tunnel. This repository alone does not prove a final cloud architecture or successful deployment. Update the architecture and README only when the team confirms and verifies its target.

## Required post-deployment checks

| Case | Expected evidence | Current cloud status |
| --- | --- | --- |
| T1 | Public app URL works | NOT RUN / not evidenced |
| T2 | Registration and login work | NOT RUN / not evidenced |
| T3 | CRUD changes PostgreSQL records correctly | NOT RUN / not evidenced |
| T4 | Restart app without losing task data | NOT RUN / not evidenced |
| T5 | /health/ succeeds | NOT RUN / not evidenced |
| T6 | Invalid input is rejected without crashing app | NOT RUN / not evidenced |
| T7 | Request or trial error appears in logs | NOT RUN / not evidenced |

Historical local testing does not change these production statuses. As recorded in [Task 05E report in PR #1](https://github.com/Anonymous06-png/cloud-task-manager/blob/task-05e-complete-ui-integration/docs/reports/step-05e-complete-ui-integration.md) on the PR branch: Chromium browser smoke was reported 19/19 PASS; Django suite 55 run / 51 pass / 4 fail. These are agent-reported PR results, not a new execution.

## Required final submissions

Git repository; live URL; PDF report (10–20 pages); slides; demo video (5–7 minutes); team assignment and contribution table; an accurate README, architecture diagram and test evidence.

For history, see docs/reports/. Older reports describe individual tasks at their original dates, not the latest runtime state.
