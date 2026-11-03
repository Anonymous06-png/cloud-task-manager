# Claude Code Project Contract

## Selected Stack

- **Backend**: Django with server-rendered templates
- **Frontend**: HTML/CSS/JavaScript (Django templates, no React/Vue)
- **Database**: PostgreSQL
- **Container**: Docker Compose
- **Deployment**: Azure Ubuntu VM with Gunicorn and Caddy

## Excluded Technologies

❌ React, Vue, Angular  
❌ JWT manual implementation (use Django sessions)  
❌ Kubernetes, Redis, Celery (unless explicitly approved)  
❌ Node.js, Express (archived for reference only)

## Work Guidelines

1. **Task-based execution**: Work on one assigned task at a time
2. **Preserve existing work**: Do not delete or modify unrelated user changes
3. **Honest reporting**: Never invent successful checks or claim tests passed without execution evidence
4. **Documentation**: Every task must save a Markdown report under `docs/reports/`
5. **No autonomous changes**: No Git staging/commits/pushes, destructive cleanup, or Azure operations without explicit approval

## Repository Structure

```
cloud-task-manager/
├── backend/             # Legacy Node.js (DO NOT USE)
├── taskmanager/         # Active Django project
├── docs/
│   ├── archive/         # Preserved implementations
│   └── reports/         # Task completion reports
├── requirements.txt     # Python dependencies
├── manage.py           # Django management
├── Dockerfile          # Python-based image
└── docker-compose.yml  # PostgreSQL + Django
```

## Environment Variables

All secrets via environment variables, never hardcoded:
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `DEBUG` - Debug mode (False in production)

## Validation Requirements

Every task must validate:
- Python syntax
- Django system checks
- Docker build success
- Report actual command output and exit codes
- Mark NOT RUN when checks are blocked

## Notes

- Node.js implementation archived in `docs/archive/legacy-node/`
- Assignment allows any framework; Django is our chosen implementation
- One unambiguous active setup (no conflicting Compose files)
