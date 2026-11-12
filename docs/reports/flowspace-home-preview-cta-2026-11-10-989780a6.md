# Home preview CTA — 2026-11-10

## Changes
- `templates/home.html`: changed only the hero’s secondary CTA from “Explore the demo” to “Preview the app”; replaced its login URL with `#demo`, targeting the existing illustrative dashboard preview through native fragment scrolling; removed the external-link arrow SVG.
- `static/css/app.css`: removed the now-unused `.demo-link .icon` sizing rule. All other CTA styling and responsive layout remain unchanged.
- `locale/vi/LC_MESSAGES/django.po`: added `Preview the app` → `Xem trước giao diện`. Retained the old demo translation because the unchanged footer still uses it.

## Verification and limitation
Source inspection confirmed the existing `id="demo"` target. No browser automation or tests were run.

Standard Django compilation was attempted with `compilemessages -l vi` and failed:

> CommandError: Can't find msgfmt. Make sure you have GNU gettext tools 0.19 or newer installed.

The existing `.mo` file was not modified; no manual binary generation or dependency installation was performed. The Vietnamese source translation is saved, but the new label will fall back to English until normal gettext compilation succeeds and the running app reloads its cached templates/translations. Scrolling and live VI rendering were not browser-verified.

No unrelated implementation changes, Git operations, commit or push. All earlier changes preserved.
