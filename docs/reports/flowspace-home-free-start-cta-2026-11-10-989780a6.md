# Home CTA update — 2026-11-10

## Scope and changes
Followed the final Home-only instructions; Login/Register were not changed.

- `templates/home.html`: removed the hero’s secondary “Preview the app” CTA. Renamed the primary CTA to **Bắt đầu miễn phí** (VI) / **Get started free** (EN), retaining `{% url 'tasks:register' %}` and the existing button classes.
- `locale/vi/LC_MESSAGES/django.po`: added `Get started free` → `Bắt đầu miễn phí`.
- Used the existing `current_language` variable for a Home-only VI label fallback because the previously attempted standard gettext compilation was blocked by missing `msgfmt`. No compiler installation or manual `.mo` generation; the compiled catalog remains unchanged.

Home layout, illustrative dashboard preview, footer, branding, themes, authentication pages, backend and CSS were left unchanged. All pre-existing changes were preserved.

## Actual verification
- **One Django system check: PASS** — `System check identified no issues (0 silenced).` Used temporary process-only environment values; no settings files or database data changed.
- **One read-only `git diff --check`: PASS** — no output or whitespace errors. No Git writes, commit or push.
- No browser automation, broad/repeated tests or translation compilation in this task. No server restart. Live rendering, cached-template refresh and CTA navigation remain for the user’s manual Brave verification.

Stopped after saving this report.
