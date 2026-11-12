# Flowspace Home UI regression fixes — 2026-11-10

## Changes

Only these implementation files were edited in this task:
- `templates/includes/workspace_preview.html`: replaced the invalid multiline `{# … #}` comment with `{% comment %} … {% endcomment %}`. The illustrative preview and localized caption remain unchanged.
- `static/css/app.css`: allow the narrow public header to wrap and grow vertically, retaining all controls; remove the forced 320px minimum specifically on Home; use continuous mobile/tablet media-query ranges to avoid fractional-width gaps; stack the hero below 1200px so the preview is not squeezed. The two-column hero at 1200px and above is unchanged.

No overflow-hiding workaround was added. Theme tokens, translations, URLs, backend, Docker, database, design references and Git history were not changed. Pre-existing work was preserved.

## Verification already completed

- Django system check: **PASS**, `System check identified no issues (0 silenced).` Used a generated process-only signing key and password-free database URL; no configuration file changes or database writes.
- Database-disallowed Django `SimpleTestCase`: **PASS**, one test with VI/EN subcases. Verified Home rendering, absence of leaked comment text, preview markup, language controls, theme/menu hooks and login/register URL markup. Used a temporary development static-storage override.
- Previously run focused patch whitespace check: **PASS**.

### Real app — port 8000

`http://127.0.0.1:8000/` reproduced the leaked comment and a 396px document width at a 375px viewport. After the initial header CSS fix and refresh, the 375px document/client widths both measured 360px, with overflow still visible and all header controls present.

The existing `runserver --noreload` process continued serving cached template text, so the comment was **still visible on port 8000**. That server was not restarted. The final minimum-width and breakpoint refinements were **not rechecked on port 8000**.

### Temporary verification — port 8001

`http://127.0.0.1:8001/` served current repository templates and CSS through a temporary Django server with a disabled database backend and process-only development settings. This was **not the real app runtime**.

- Fresh VI Home snapshots contained no leaked comment.
- Final layout measurements passed at **320, 375, 430, 639, 640, 768, 1023, 1024, 1199, 1200, 1280 and 1440px**: document `scrollWidth` equalled `clientWidth`; dashboard and task-main internal widths also matched, without clipping. HTML/body `overflow-x` remained `visible`.
- VI/Light desktop screenshot at 1440px showed the intact two-column design and no leaked comment. Final mobile verification was DOM/geometry-based; no post-refinement mobile screenshot was captured.

## Remaining limitations and stop state

- Browser evidence came from the ZCode in-app browser, **not Brave**. Final acceptance in the real Brave/port-8000 runtime remains outstanding.
- A theme-toggle click timed out; Dark rendering/toggle operation was not verified. Browser EN switching and end-to-end CTA/menu navigation were not completed; only their template hooks/URLs were checked.
- Initial shell checks lacked `SECRET_KEY`/`DATABASE_URL`; temporary values resolved those prerequisites. The first template test failed with `Missing staticfiles manifest entry for 'flowspace/favicon.svg'`; the development-storage rerun passed. Production static collection was not run or changed.
- One rendering-tool wait also timed out; later current-state measurements completed successfully.
- At the user's stop instruction, all further browser automation, tests and exploration ceased. The temporary port-8001 task was stopped; the real port-8000 server was left untouched. No Git operations followed that instruction. No commit or push was made.
