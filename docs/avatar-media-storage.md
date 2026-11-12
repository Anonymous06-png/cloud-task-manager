# Profile avatar media

Avatars require Pillow (pinned in requirements) and Django default storage. The local default is `BASE_DIR / 'media'`, already ignored by Git. Inputs: JPG/JPEG, PNG or WebP, at most 2 MiB (2 × 1024² bytes), at most 4096 pixels per side. Actual content is verified and fully decoded; MIME is not trusted. Images are reduced to at most 512 pixels per side and re-encoded as metadata-free, single-frame PNGs with random UUID filenames. Originals are never saved. Failed validation leaves the previous image untouched.

Only authenticated owners can POST upload/change/remove or GET their avatar. The image URL accepts no filename/user identifier, looks up `request.user.profile`, and streams through Django storage with PNG type, nosniff and private/no-store headers. `MEDIA_URL` is not publicly routed, even in development; no arbitrary media-directory or production file-serving route is added.

Replacement/removal deletes the previous file after database commit; rollback of the avatar save attempts cleanup of the newly written file. Database and object/file storage are not one atomic system: a process crash/storage outage can leave orphan files. Post-commit cleanup failures are logged, not allowed to invalidate a successful DB update. Monitor these logs and reconcile unreferenced files separately with a reviewed retention policy. Direct model edits/account deletion are not avatar UI operations and require storage reconciliation as well. Do not run broad file cleanup against live storage.

## Docker / production prerequisites (not configured or verified here)

The existing Docker configuration persists static assets, **not uploaded media**. Container-local avatar files can be lost on replacement/recreation. Before production use, provision a persistent private media volume at the configured `MEDIA_ROOT`, or configure a private persistent Django-compatible storage backend. Ensure service-account write/read/delete permissions; include files and profile DB references in coordinated backups/restores. Do not serve the media directory as executable content or expose an unrestricted public media root. The authenticated image endpoint supports private storage without public object URLs.

No Docker/DevOps configuration was changed. Volume lifecycle, remote storage, backup/restore and container recreation durability remain **NOT VERIFIED**. These are deployment prerequisites, not claims that current Docker persistence works.
