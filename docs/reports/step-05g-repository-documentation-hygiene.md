# Repository documentation hygiene — 2026-11-04

## Scope and environment
GitHub repository Anonymous06-png/cloud-task-manager, based on main. Read-only inspection of both main and the open Task 05E branch, the official six-page assignment PDF and the project handoff. This task changes **documentation and Docker build-context exclusions only**, not Django behavior, tests, the database, archive files or cloud resources.

## Inventory findings
- main had 39 agent reports under docs/reports/ and five Figma PNG exports under docs/design/figma-exports/.
- Root backend/ is inactive Node.js code duplicated in docs/archive/legacy-node/. Both were deliberately left untouched.
- README.md described CRUD and filtering as planned, even though local reports and implementation include them.
- docs/requirements.md described Task 04/05 as not started.
- CLAUDE.md pointed to a nonexistent active Django taskmanager/ path instead of config/ and tasks/.
- Open PR #1 contains the redesigned UI. main and PR #1 diverged, so UI changes must not be silently represented as merged.
- .dockerignore included old archives but still allowed unnecessary documentation and root legacy code into the Docker build context.

## Files changed
- README.md: update application state, clear distinction between existing source and unverified production, reproduction commands and repository navigation.
- docs/requirements.md: update requirement/evidence tracker; mark production T1–T7 as not evidenced.
- CLAUDE.md: correct current structure and agent verification/permission constraints.
- .dockerignore: exclude docs/, backend/ and tools/ from Docker build context; Dockerfile only copies explicit Django source folders.

No reports, Figma screenshots, legacy code or PDF were deleted or moved. This is intentionally a conservative cleanup pending explicit approval for historical-file removal.

## Commands and verification
- GitHub API tree/file inspection of main and Task 05E branch: completed.
- Repository changes created through GitHub APIs on a new review branch: see corresponding PR and commit.
- Runtime commands, Docker builds, tests and browser checks: NOT RUN; this review did not have access to the user's Windows environment.
- Git status on the user's Windows machine: NOT RUN / unavailable.
- GitHub API operations do not report shell exit codes; do not infer them.

## Remaining risks and next allowed step
Review this documentation-only PR. Do not merge automatically. UI PR #1 remains independent and still needs review; its agent report lists four stale text assertions. Future optional cleanup can move older reports into an archive or remove the duplicate top-level Node backend **only after explicit confirmation**; preserve grading evidence and Git history.
