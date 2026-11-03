# Cloud Task Manager

Personal task management web application deployed on cloud infrastructure.

**Project Status**: In Development

## Team Members
- [Member names will be added]

## Overview
A web application for managing personal tasks with user authentication, CRUD
operations, and cloud deployment. Built with Django server-rendered templates
(no JavaScript SPA framework).

## Features
- User registration and login (Django sessions, server-side protected pages)
- Add, view, update, and delete tasks (planned)
- Filter tasks by completion status (planned)
- Persistent PostgreSQL storage
- Health check endpoint for monitoring
- Dockerized deployment

## Technology Stack
- **Backend**: Python 3.11, Django 5.2 LTS
- **Frontend**: Django templates, HTML, CSS
- **Database**: PostgreSQL 16
- **Container**: Docker / Docker Compose
- **WSGI server**: Gunicorn
- **Reverse proxy / TLS**: Caddy (production)
- **Cloud Platform**: Azure Ubuntu VM (planned)

## Architecture

```
[User] -> [Caddy HTTPS] -> [Gunicorn/Django] -> [PostgreSQL]
                                   |
                            [Health: /health/]
```

## Local Development (container-first)

All runtime verification is done with Docker Compose so that the local machine
does not need Python or Django installed.

### Prerequisites
- Docker Desktop (Docker Engine + Compose)
- Git

### Configure required variables

Required variables: `SECRET_KEY` and `POSTGRES_PASSWORD`. Compose stops with a
clear error if either is unset or empty.

```powershell
# 1. Create the environment file from the template
Copy-Item .env.example .env
```

Then edit `.env` and set:

- `SECRET_KEY` - generate a value and paste it in (do not commit `.env`):
  ```powershell
  python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
  ```
- `POSTGRES_PASSWORD` - choose a strong password.

`DJANGO_ENV=local` is the default for this stack, so the app serves plain HTTP
on `127.0.0.1` without a TLS listener.

### Run the stack

```powershell
docker compose up --build -d
```

Access the application:
- Home: http://127.0.0.1:8080/
- Register: http://127.0.0.1:8080/register/
- Login: http://127.0.0.1:8080/login/
- Dashboard (login required): http://127.0.0.1:8080/dashboard/
- Health check (public): http://127.0.0.1:8080/health/

The app port is bound to `127.0.0.1:8080` only. PostgreSQL is not published to
the host; it is reachable only on the internal Compose network.

### Check status and logs

```powershell
docker compose ps
docker compose logs app
```

### Run the automated tests (inside the app container)

```powershell
docker compose exec app python manage.py check
docker compose exec app python manage.py test
```

## Building the Docker Image

```powershell
docker compose build
```

## Persistence verification (validation test T4)

This compares an identifiable test record before and after restarting the
application container. It runs entirely through Compose and does not print the
database password.

```powershell
# 1. Write an identifiable marker
docker compose exec db psql -U taskuser -d taskmanager -c "CREATE TABLE IF NOT EXISTS persist_check (marker text);"
docker compose exec db psql -U taskuser -d taskmanager -c "INSERT INTO persist_check (marker) VALUES ('task02c-persist-marker');"

# 2. Record the marker value before restart
docker compose exec db psql -U taskuser -d taskmanager -c "SELECT marker FROM persist_check;"

# 3. Restart only the application container
docker compose restart app

# 4. Confirm the same marker value is still present
docker compose exec db psql -U taskuser -d taskmanager -c "SELECT marker FROM persist_check;"
```

Expected: `task02c-persist-marker` is present after the restart. Once task CRUD
exists, replace the marker table with an application-created task row.

## Cloud Deployment (production)

Production serves HTTPS via Caddy on the Azure Ubuntu VM. The same image is used
with a production environment:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Required Django signing key (from a secrets manager) |
| `POSTGRES_PASSWORD` | Required database password |
| `DATABASE_URL` | `postgresql://user:password@host:5432/dbname` |
| `DJANGO_ENV` | `production` |
| `SECURE_SSL_REDIRECT` | `True` (HTTPS enforced; `/health/` stays exempt) |
| `ALLOWED_HOSTS` | Public hostname(s) |

### Deployment Steps
1. Create cloud resources (VM, managed database).
2. Configure security groups and firewall rules (expose only 80/443 and SSH).
3. Provide environment variables through the platform's secrets manager.
4. Set `DJANGO_ENV=production` and `SECURE_SSL_REDIRECT=True`.
5. Deploy the Docker image and run migrations.
6. Verify `/health/` and review logs.

Detailed steps will be added after platform setup.

## Testing

### Validation Test Cases

| ID | Test Scenario | Expected Result |
|----|---------------|-----------------|
| T1 | Access public URL | Web page displays normally |
| T2 | Register and login | User accesses personal functions |
| T3 | Add, edit, delete task | Data changes correctly in database |
| T4 | Restart application | Data persists (see Persistence verification) |
| T5 | Call `/health/` | Returns success status |
| T6 | Send invalid data | Application handles error appropriately |
| T7 | View logs | Find experimental requests or errors |

## Monitoring

- Application logs viewable through the cloud platform (`docker compose logs app`).
- Health check endpoint: `/health/`.
- Metrics tracked: [To be specified after deployment]

## Cost Estimation
[Monthly cost breakdown will be added after deployment]

## Cleanup Instructions

### Destroying Cloud Resources
1. Stop compute instances/containers.
2. Delete database instances.
3. Release static IPs.
4. Remove unused disks.
5. Delete security groups (if no longer needed).

## Project Structure

```
cloud-task-manager/
├── config/               # Django project (settings, urls, wsgi)
├── tasks/                # Tasks app (models, views, urls, tests)
├── templates/            # Django templates
├── static/               # Project static files (tracked via .gitkeep)
├── docs/
│   └── reports/          # Task reports
├── backend/              # Legacy Node.js (archived, DO NOT USE)
├── docs/archive/legacy-node/   # Archived Node.js reference
├── .env.example          # Environment variable template
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── README.md
```

## Security Notes
- Never commit:
  - `.env` files
  - Passwords or access keys
  - Private keys (`.pem`, `.key`)
  - Database connection strings with credentials
- Required secrets fail fast at startup instead of defaulting to empty.
- PostgreSQL is not published to the host.

## License
MIT

---
**Cloud Computing Project** | [University/Course Name]
