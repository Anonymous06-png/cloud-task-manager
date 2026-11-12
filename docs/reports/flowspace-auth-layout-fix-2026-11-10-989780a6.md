# Flowspace authentication layouts — 2026-11-10

## Changes
- `templates/registration/login.html` and `templates/registration/signup.html`: removed the illustrative dashboard include from both authentication pages. Page titles now use the existing translated “Log in” / “Create account” labels followed by `| Flowspace`, removing Register’s outdated Workspace branding.
- `static/css/app.css`: changed `.workspace-login` to a centered, single-column layout with `width: 100%` and the existing 400px form width cap. Removed the mobile 520px width override so the same cap applies consistently.

Preserved every form field, field include, non-field error output, CSRF token, POST action, submit hook, login `next` field and navigation link. Existing VI/EN translation tags and Flowspace theme styling remain intact; no new translation strings were required. Home and its dashboard preview, backend and all earlier changes were left untouched.

## Actual verification
- **One Django system check: PASS** — `System check identified no issues (0 silenced).` Used temporary process-only environment values; no configuration files or database data changed.
- **One read-only `git diff --check`: PASS** — no whitespace errors. Git emitted this line-ending warning: `in the working copy of 'templates/registration/signup.html', LF will be replaced by CRLF the next time Git touches it`. No line-ending normalization or Git writes were performed.
- No browser automation, broad/repeated tests, authentication submissions, translation compilation or server restart. Live layout, VI/EN rendering and authentication behavior remain for manual Brave verification; a running server may still have cached templates.

No commit or push. Stopped after saving this new report.
