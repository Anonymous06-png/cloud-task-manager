# Project Requirements Documentation

## Assignment Requirements (from PDF)

Source: `docs/Project-Cloud-Computing.pdf` (6 pages, Vietnamese)

### Mandatory Application Features

1. ✅ User account creation and login
2. ✅ Add new tasks
3. ✅ View task list
4. ✅ Update task (name, description, deadline, status)
5. ✅ Delete tasks
6. ✅ Filter by status: "Not completed" and "Completed"
7. ✅ Persistent database storage

### Mandatory Technical Components

**Application**:
- Web interface with server-side processing
- Any language/framework allowed ✅
- Health check endpoint (e.g., `/health`) ✅
- Sample data for testing

**Docker**:
- Dockerfile for containerization ✅
- Image must build and run on other machines
- No secrets in Git ✅
- Encouraged: .dockerignore, versioned tags

**Cloud Infrastructure**:
| Component | Requirement | Our Implementation |
|-----------|-------------|-------------------|
| Compute | VM/container/PaaS | Azure Ubuntu VM (planned) |
| Database | PostgreSQL/MySQL/MongoDB | PostgreSQL ✅ |
| Observability | Logs + ≥1 metric | Planned |

**Security**:
- Only expose necessary ports ✅
- Secrets via environment variables ✅
- MFA enabled on cloud account (user responsibility)
- Budget alerts/cost monitoring (planned)
- Non-root operations where possible ✅

### Deliverables

1. Git repository link
2. Live application URL (public)
3. PDF report (10-20 pages)
4. Presentation slides
5. Demo video (5-7 minutes)
6. Task distribution table

### Validation Tests (Section 5, Page 3)

| ID | Scenario | Expected |
|----|----------|----------|
| T1 | Access public URL | Page displays normally |
| T2 | Register and login | User accesses personal features |
| T3 | Add/edit/delete task | Data changes in database |
| T4 | Restart application | Data persists |
| T5 | Call `/health` | Returns success status |
| T6 | Send invalid data | Error handled appropriately |
| T7 | View logs | Find test requests/errors |

### Bonus Points (Max total: 10/10)

- CI/CD pipeline: +0.5
- HTTPS + custom domain: +0.25
- Database backup/recovery: +0.25
- Infrastructure as Code (Terraform): +0.5
- Load testing: +0.25

---

## Our Implementation Decisions

### Selected Stack

**Decision Date**: 2026-10-17

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python | Team familiarity, Django ecosystem |
| Framework | Django 5.2 LTS | Built-in admin, ORM, auth, templates |
| Database | PostgreSQL 16 | Required by assignment |
| Container | Docker Compose | Local dev + production consistency |
| Web server | Gunicorn | Production-ready WSGI server |
| Reverse proxy | Caddy | Automatic HTTPS |
| Cloud | Azure | Single Ubuntu VM for compute |

### Excluded Options

- ❌ Node.js/Express - Initial implementation, replaced with Django
- ❌ JWT manual auth - Use Django sessions instead
- ❌ React/Vue - Assignment emphasizes deployment, not complex frontend
- ❌ Kubernetes - Over-engineered for single-VM requirement
- ❌ Microservices - Monolith appropriate for this scale

### Implementation Status

**Completed**:
- ✅ Repository structure
- ✅ Git initialized with proper .gitignore
- ✅ Node.js implementation archived
- ✅ CLAUDE.md contract established
- ✅ Django project foundation (files present, syntax-valid; runtime
  verification pending — see `docs/reports/step-02b-foundation-verification.md`)
- ✅ User authentication (register / login / logout, Django sessions,
  CSRF protected forms, protected personal area) — see
  `docs/reports/step-03-authentication.md`

**Not Started**:
- ⏳ Task CRUD operations (Task 4)
- ⏳ Frontend templates (Task 5)
- ⏳ Cloud deployment (Task 6)
- ⏳ Observability setup (Task 7)
- ⏳ Validation tests T1-T7 (Task 8)

**Known Issues**:
- Frontend folder currently empty
- No sample data yet
- Architecture diagram not created
- Deployment documentation incomplete
- Docker/PostgreSQL runtime verification blocked (daemon unavailable) — see `docs/reports/step-02b-foundation-verification.md`
- Local Python is 3.14.3; container Python 3.11 is compatible with Django 5.2 LTS. Use the container for runtime checks

### Assumptions & Constraints

**Assumptions**:
1. Single-user prototype acceptable for grading
2. Basic auth (username/password) sufficient
3. Simple HTML/CSS UI acceptable (not polished design)
4. Manual deployment acceptable (CI/CD is bonus)

**Constraints**:
1. Must be accessible via public URL at grading time
2. Budget monitoring required
3. No secrets in repository
4. Must document cost estimates

### Validation Strategy

Each task will verify:
1. Python syntax via `python -m py_compile`
2. Django checks via `python manage.py check`
3. Docker build success
4. Container health checks
5. HTTP endpoints respond correctly

**Never claim**:
- Tests passed without execution logs
- Build succeeded without exit code 0
- Database migrated without `showmigrations` output

---

## References

- Assignment PDF: `docs/Project-Cloud-Computing.pdf`
- Legacy Node.js: `docs/archive/legacy-node/`
- Task reports: `docs/reports/`
