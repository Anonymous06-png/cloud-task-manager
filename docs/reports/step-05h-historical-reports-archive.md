# Task 05H — Archive superseded engineering reports

**Date:** 2026-11-04
**Repository:** Anonymous06-png/cloud-task-manager
**Scope:** documentation organization only; GitHub API branch and PR.

## Changes

- Moved **23** old reports from docs/reports/ to docs/archive/reports/ using the **same Git blob SHAs**. Original bytes are retained; no report was rewritten.
- Kept **16** evidence/referenced reports in docs/reports/, plus added this new report and reports/README.md.
- Added docs/README.md, docs/design/README.md and docs/archive/reports/README.md.
- Left Django source, configuration, official PDF, Figma exports, static prototype, root backend/ and the existing legacy Node archive unchanged.
- Did not merge PR #1 (UI) or PR #2 (prior docs hygiene). This proposal is independent of those PRs and targets main.

## Verification

- GitHub main recursive tree: 39 original reports; 23 to archive, 16 kept; tree not truncated.
- Checked top-level README, CLAUDE.md, docs/requirements.md, relevant design documentation and 16 kept report references; retained referenced reports in place.
- Scanned all 23 moved reports for relative Markdown links to avoid breaking active reference paths.
- Identical inactive Node.js blobs (five root backend/ vs docs/archive/legacy-node/backend/) observed, but **no deletion** was authorized/performed.
- GitHub tree/blob SHA checks after publishing can confirm the archive is lossless.
- Windows shell/Django runtime, Docker build, test suite and browser checks: **NOT RUN** (docs-only task; no Windows machine access).
- Shell commands and exit codes: **NOT RUN**; performed through GitHub API, not shell. No fabricated counts.
- Existing local Git working tree status: **NOT RUN / unavailable**.

## Risks

- Old external links directly to moved docs/reports paths may no longer resolve on the new main snapshot after merge; Git history still retains earlier paths.
- Archived text can contain historical commands and stale environment assumptions; not an instruction to run them.
- Follow-up merge of UI PR #1 and docs PR #2 is a separate review decision.

## Git status and next allowed step

One new review branch/PR; no force, reset, merge or local working-tree changes. Verify GitHub branch PR before acceptance. The root Node.js duplicate can be addressed in another task with **explicit deletion authorization** after inspecting deployment references. Do not remove docs/archive/legacy-node/.
