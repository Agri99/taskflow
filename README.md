# TaskFlow

TaskFlow is a **full-stack project management application** built to demonstrate real-world engineering practices: RBAC enforced at the query layer, soft deletion with saga patterns, background task processing, immutable audit logging, test-driven development, and a React SPA consuming a versioned REST API.

This project is **backend-first by design** — the Django backend enforces all business rules, and the React frontend is a faithful consumer of those rules, not a duplicator of them.

This is designed as an internal tool where admins provision accounts. For public-facing deployment, a registration system would be added.

---

## Project Goals

- Write **production-style Django code**, not tutorial snippets
- Enforce permissions at the **model / queryset layer** (single source of truth)
- Use **tests to drive behavior** and protect invariants
- Implement **RBAC (Role-Based Access Control)** with proper permission mapping
- Maintain an **immutable audit trail** of critical actions
- Process **background tasks** asynchronously with Celery + Redis
- Build a **React SPA** that consumes the API with JWT authentication, optimistic UI updates, and RBAC-aware rendering

---

## Architecture & Tech Stack

**Backend**
- **Framework:** Django 6
- **Database:** PostgreSQL (Docker)
- **Task Queue:** Celery with Redis broker
- **Scheduler:** Celery Beat (periodic tasks)
- **DevOps:** Docker, Docker Compose, GitHub Actions (CI)
- **RBAC:** Django `Permission` model + custom Role & Membership layer
- **Audit:** GenericForeignKey-based immutable audit log
- **API Layer:** Django REST Framework with JWT authentication (simplejwt)
- **API Documentation:** drf-spectacular (Swagger UI at `/api/docs/`)
- **Testing:** pytest + pytest-django, Django test client + DRF APIClient

**Frontend**
- **Framework:** React 19 (Vite)
- **Routing:** React Router v7
- **HTTP Client:** Axios with request/response interceptors
- **Auth:** JWT stored in localStorage, silent token refresh via interceptor
- **State:** `useState`, `useEffect`, custom hooks (`useFetch`, `usePagination`)

**Design Principles**
- Single source of truth for permissions (QuerySets + Model methods)
- Business rules live on the server; frontend is a consumer, not an enforcer
- Fail-safe defaults: soft delete + purge, 404 over 403 to avoid leaking presence
- API views are separate from Django views: `api_views.py` handles JSON for external clients while `views.py` handles HTML. Business logic lives in models so both layers share the same rules without duplication
- Async task processing with saga patterns: transactional rollback on notification failures
- React components are consumers of backend rules, not enforcers — permission checks in the UI are UX conveniences, not security boundaries

---

## Prerequisites

Before running TaskFlow, ensure you have:

- **Docker Desktop** (Windows/Mac) or Docker Engine + Docker Compose (Linux)
- **Git** for version control
- **Node.js 18+** (for local frontend development outside Docker)
- **Windows users:** Git Bash or WSL2 recommended for command-line tools

**Note:** You do NOT need to install Python, PostgreSQL, Redis, or Celery locally. Docker handles all of that.

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/taskflow.git
cd taskflow
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (default values work for local development).

### 3. Start All Services

```bash
docker compose up --build
```

This starts:
- **Django** (backend API on `http://localhost:8000`)
- **React** (frontend on `http://localhost:5173`)
- **PostgreSQL** (database)
- **Redis** (message broker)
- **Celery Worker** (background task processor)
- **Celery Beat** (scheduled task scheduler)

### 4. Run Migrations & Create Superuser

In a new terminal:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 5. Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api/v1/
- **Django Admin:** http://localhost:8000/admin/
- **API Docs:** http://localhost:8000/api/docs/

---

## Background Tasks (Celery + Redis)

TaskFlow uses **Celery** for asynchronous task processing and **Redis** as the message broker.

### Implemented Tasks

**Email Notifications:**
- `notify_org_members_new_task` — Sends email when a task is created
- Uses **saga pattern**: if notification fails, task creation is rolled back

**Scheduled Cleanup:**
- `purge_old_deleted_comments` — Runs daily via Celery Beat
- Permanently deletes soft-deleted comments older than 30 days
- Logs audit entries for each purged comment

### Monitoring Tasks

```bash
# View Celery worker logs
docker compose logs -f celery_worker

# View Celery Beat scheduler logs
docker compose logs -f celery_beat

# View Redis connection status
docker compose exec redis redis-cli ping
```

### Testing Tasks Manually

```bash
docker compose exec web python manage.py shell

>>> from tasks.tasks import notify_org_members_new_task
>>> result = notify_org_members_new_task.delay(task_id=1)
>>> result.get(timeout=10)  # Wait for result
```

---

## RBAC (Role-Based Access Control)

TaskFlow implements a production-grade RBAC system that separates business rules from administrative permissions.

### Architecture

**Core Models:**
- **Role**: Named collection of Django permissions (e.g., "Moderator", "Auditor")
- **Membership**: Assigns users to roles (many-to-many through table)
- **Permissions**: Fine-grained Django permissions (e.g., `comments.delete_comment`)

**Permission Resolution:**
```python
# Business Rule (hardcoded, always applies)
if comment.author == user:
    return True  # Authors can always delete their own comments

# RBAC Permission (dynamic, role-based)
if user_has_perm(user, 'comments.delete_comment'):
    return True  # Moderators can delete any comment
```

### Key Features

- **Flexible role assignment** — Change permissions without code changes
- **Single source of truth** — Permissions checked in model layer
- **Organization-scoped** — Each org has isolated data
- **Superuser override** — Admins can access cross-org audit logs
- **JWT claim injection** — `can_view_audit` baked into the JWT payload at login
- **RBAC-aware React UI** — Audit link only visible to permitted users

### Setting Up Roles

**1. Create a Role (via Django admin):**
```
/admin/rbac/role/add/
- Name: Moderator
- Slug: moderator (auto-filled)
- Permissions: Select "Can delete comment"
```

**2. Assign Role to User:**
```
/admin/rbac/membership/add/
- User: Select user
- Role: Select "Moderator"
```

**3. Verify:**
User can now delete ANY comment in their organization (not just their own).

### Example Roles

**Moderator:**
- `comments.delete_comment` — Remove inappropriate comments
- `rbac.view_auditentry` — Monitor user actions

**Auditor:**
- `rbac.view_auditentry` — Read-only access to audit logs

**Content Manager:**
- `tasks.add_task`
- `tasks.change_task`
- `tasks.delete_task`
- `comments.delete_comment`

### Testing RBAC

```bash
docker compose exec web pytest rbac/tests/test_rbac_integration.py -v
```

---

## Audit Logging System

TaskFlow records an **immutable audit trail** of all critical actions.

### What Gets Logged

- Comment created (`Comment.create_with_audit()`)
- Comment edited (`comment.apply_edit()`)
- Comment deleted (`comment.soft_delete()`)
- Task deleted (`task.soft_delete()`)
- Comments purged by Celery Beat (`purge_old_deleted_comments` task)

### Audit Entry Structure

| Field | Description |
|-------|-------------|
| `actor` | User who performed the action (null for system actions) |
| `action` | One of: `create`, `edit`, `delete`, `purge` |
| `target` | The object that was modified (GenericForeignKey) |
| `timestamp` | When the action occurred (indexed) |
| `payload` | JSON metadata (e.g., `{"old": "...", "new": "..."}`) |
| `organization` | Organization scope (for data isolation) |

### Viewing Audit Logs

**Django Admin (Read-Only):** `/admin/rbac/auditentry/`

**React UI:** `/rbac/audit` — requires `rbac.view_auditentry` permission. The Audit link in the task list only appears for users whose JWT contains `can_view_audit: true`.

**REST API:** `GET /api/v1/rbac/audit/`

### Security & Immutability

- Audit entries use `editable=False` in admin
- No `add_auditentry` or `change_auditentry` permissions granted to any role
- `delete_auditentry` disabled for all users
- Append-only by design

---

## REST API

TaskFlow exposes a versioned REST API at `/api/v1/` using JWT authentication.

### Authentication

```bash
# Get tokens
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_user", "password": "your_pass"}'

# Use access token
curl http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

The JWT payload includes a custom `can_view_audit` claim injected via `CustomTokenObtainPairSerializer`.

### Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|------------|
| POST | `/api/v1/auth/login/` | Get JWT tokens | Public |
| POST | `/api/v1/auth/refresh/` | Refresh access token | Public |
| GET/POST | `/api/v1/tasks/` | List/create tasks | Authenticated |
| GET/PATCH/DELETE | `/api/v1/tasks/<id>/` | Task detail | Authenticated |
| GET/POST | `/api/v1/tasks/<id>/comments/` | List/create comments | Authenticated |
| GET/PATCH/DELETE | `/api/v1/tasks/<id>/comments/<id>/` | Comment detail | Authenticated |
| GET | `/api/v1/rbac/audit/` | Audit log | `rbac.view_auditentry` |

**Interactive Docs:** `/api/docs/` (Swagger UI)

---

## React Frontend

The React frontend lives in `taskflow-frontend/` and is a separate Vite project that consumes the Django API.

### Features

- **JWT authentication** with silent token refresh via Axios interceptors
- **Protected routes** — unauthenticated users redirected to `/login` with return path preserved
- **Permission-gated routes** — audit log only accessible to users with `can_view_audit` in their JWT
- **Task list** with load-more pagination
- **Task detail** with nested comments
- **Full comment CRUD** — create, inline edit (within 15-minute window), soft delete
- **Task creation modal** with controlled forms
- **Optimistic UI** — comments appear/disappear instantly without page reload
- **RBAC-aware UI** — edit/delete buttons only shown to the comment author within the permitted window

### Project Structure

```
taskflow-frontend/src/
├── components/
│   ├── AuditLog.jsx       ← permission-gated audit view
│   ├── CommentForm.jsx    ← comment creation form
│   ├── Login.jsx          ← JWT login with redirect-back
│   ├── ProtectedRoute.jsx ← token + optional permission check
│   ├── TaskDetail.jsx     ← task + comments + CRUD
│   ├── TaskFormModal.jsx  ← controlled form for task creation
│   └── TaskList.jsx       ← paginated task list
├── hooks/
│   ├── useFetch.js        ← generic single-resource fetch hook
│   └── usePagination.js   ← paginated list fetch hook with load-more
└── services/
    ├── api.js             ← all API call functions
    └── axiosInstance.js   ← configured Axios with auth + refresh interceptors
```

### Running Frontend Separately (Optional)

If you want to develop the frontend outside Docker:

```bash
cd taskflow-frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`. Django must be running on `http://localhost:8000`.

---

## Permissions Overview

| Action | Comment Author | Task Owner | Other Users |
|--------|----------------|------------|-------------|
| Create comment | ✅ | ✅ | ❌ |
| Edit comment (within window) | ✅ | ❌ | ❌ |
| Delete comment | ✅ | ✅ | ❌ |

Additional rules:
- Deleted comments cannot be edited or deleted again
- Edited state is derived from `edited_at` (no duplicated boolean field)
- UI visibility is driven by flags computed in views, not templates
- Edit window is enforced both server-side (model) and client-side (UX only)

---

## Testing

### Run All Tests

```bash
docker compose exec web pytest
```

### Run Specific Test Files

```bash
docker compose exec web pytest comments/tests/test_comment_permissions.py -v
docker compose exec web pytest rbac/tests/test_rbac_integration.py -v
docker compose exec web pytest tasks/tests/test_celery_tasks.py -v
```

### Testing Philosophy

- Tests describe **behavior**, not implementation details
- Boundary conditions are explicitly tested:
  - Exact edit-window cutoff
  - Attempted edits after deletion
  - Re-edit attempts not overwriting `edited_at`
- Unauthorized access returns **404** to prevent information leakage
- RBAC permission matrices tested to ensure correct role enforcement
- Audit tests ensure critical actions create immutable audit entries
- Celery tasks tested with mock email backends

---

## Development Workflow

### Making Changes

1. **Edit code** in your local editor (changes sync to Docker via volume mounts)
2. **Django auto-reloads** when you save Python files
3. **React hot-reloads** when you save frontend files
4. **View logs** with `docker compose logs -f web` or `docker compose logs -f frontend`

### Running Management Commands

```bash
docker compose exec web python manage.py <command>
```

Examples:
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py shell
```

### Accessing Containers

```bash
# Django shell
docker compose exec web python manage.py shell

# PostgreSQL shell
docker compose exec db psql -U taskflow_user -d taskflow_db

# Redis CLI
docker compose exec redis redis-cli

# Bash inside web container
docker compose exec web bash
```

### Stopping Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes database)
docker compose down -v
```

---

## Troubleshooting

### "Connection refused" or "getaddrinfo failed" errors

**Problem:** Django can't connect to Redis or PostgreSQL.

**Solution:** Make sure all services are running:
```bash
docker compose ps
```

If a service is down, restart it:
```bash
docker compose up -d
```

### Celery tasks not running

**Check worker is running:**
```bash
docker compose logs celery_worker
```

**Manually trigger a task:**
```bash
docker compose exec web python manage.py shell

>>> from tasks.tasks import notify_org_members_new_task
>>> result = notify_org_members_new_task.delay(1)
>>> result.get(timeout=10)
```

### Task creation returns 500 error

**Cause:** Notification task failed due to missing Celery worker or Redis.

**Solution:** Ensure `celery_worker` and `redis` containers are running in `docker compose ps`. If running Django manually (outside Docker), you MUST also run Redis and Celery worker manually — Docker is the recommended approach.

### Frontend not connecting to backend

**Check ports:**
- Frontend should be on `http://localhost:5173`
- Backend should be on `http://localhost:8000`

**Check CORS settings** in `taskflow/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]
```

### Database reset needed

```bash
docker compose down -v
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## Project Highlights

- Task model with ownership and secure `TaskDetailView` access
- Comment system with:
  - Create / edit / soft-delete behavior
  - **Edit window** enforcement (`COMMENTS_EDIT_WINDOW_MINUTES`)
  - **FIRST_EDIT_ONLY** semantics — `edited_at` set once on first successful edit
  - `(edited)` badge derived from `edited_at` (no boolean duplication)
- Permission design:
  - Model & QuerySet-driven helpers (`editable_by`, `deletable_by`, `can_be_*`)
  - Views use `get_queryset()` and view-level flags for presentation
- Background task processing:
  - Email notifications with saga pattern rollback on failure
  - Scheduled comment purging via Celery Beat
  - Immutable audit trail of all purge operations
- Developer experience:
  - Dockerized dev environment with hot-reload for Django and React
  - CI: GitHub Actions runs tests on push/PR
  - Tests use `pytest` / `pytest-django` and cover edge cases

---

## Key Settings

```python
COMMENTS_EDIT_WINDOW_MINUTES = 15  # Controls edit window for comments
CELERY_BROKER_URL = 'redis://redis:6379/0'  # Docker DNS name 'redis'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_BEAT_SCHEDULE = {
    'purge-old-deleted-comments': {
        'task': 'tasks.tasks.purge_old_deleted_comments',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

---

## Lessons Learned

### Backend

- **Model-driven rules scale better than view-driven checks.** Putting permissions in QuerySets prevents duplication and accidental leaks.
- **Derived state is preferable to duplicate flags.** `edited_at` as the source of "edited" avoids drift and keeps tests simple.
- **Tests catch integration surprises early.** Moving to an environment-based settings layout revealed template path and redirect assumptions that were otherwise hidden.
- **Containerized dev + CI = reproducible engineering.** Docker + GitHub Actions ensured the same tests run in dev and CI, surfacing env-specific issues quickly.
- **RBAC centralizes authorization.** Roles can be modified without touching code, making permission management scalable.
- **Audit trails require immutability.** Admin interfaces must be carefully configured to prevent tampering with historical records.
- **Model-level business logic makes security reusable.** By implementing `soft_delete()` and `apply_edit()` in the models, every interface — Django views, API endpoints, future integrations — automatically inherits the same rules.
- **Serializers translate data; they should not enforce policy.** Business rules like edit-window validation belong in the model, not the serializer.
- **Configuration errors often fail silently.** The `COMMENT_EDIT_WINDOW_MINUTES` vs `COMMENTS_EDIT_WINDOW_MINUTES` typo disabled a feature without raising an error. Automated tests are critical.
- **Authentication mechanisms encode architectural tradeoffs.** Session auth keeps state on the server and supports true logout. JWT shifts state to the client, simplifying server infrastructure but making token invalidation significantly harder.
- **URL separation reflects long-term architecture.** Maintaining `api_urls.py` separately from `urls.py` isolates API contracts from the browser interface.
- **Saga patterns prevent orphaned data.** Rolling back task creation when notification fails ensures the database stays consistent — better to show an error than leave a task in a "notification pending" state forever.
- **Async task systems introduce distributed failure modes.** A background task failure (Redis down, Celery worker crashed, email service timeout) can cascade into user-facing errors if not handled defensively. Saga patterns and retry logic are essential.
- **Docker networking is a different namespace.** Service names like `redis` resolve inside Docker's internal DNS but fail outside it. Running partial infrastructure (Django without Docker, but Celery needs Redis) leads to confusing "connection refused" errors.

### Frontend

- **The frontend is a consumer of backend rules, not a co-enforcer.** Edit and delete buttons are a UX convenience — Django enforces the actual permission on every request. Never assume the frontend is a security layer.
- **Axios interceptors are middleware for HTTP.** Centralizing auth header attachment and 401 handling in one place eliminates repetition and makes token refresh transparent to the rest of the app.
- **Optimistic UI requires understanding failure modes.** Updating state before the API responds feels fast, but you must handle the case where the API call fails and roll back the change.
- **Custom hooks enforce separation of concerns.** `useFetch` and `usePagination` extract data-fetching logic out of components, making components responsible only for rendering.
- **JWTs can carry custom claims.** Baking `can_view_audit` into the token at login avoids an extra API call to determine permissions on the frontend. The tradeoff is that the claim is stale until the next login.
- **`useState` is watched by React; plain variables are not.** This distinction is the core of why React re-renders work the way they do.
- **SPAs need routing discipline.** React Router's `state` prop on `<Navigate>` enables redirect-back-after-login, which requires deliberate implementation — it doesn't happen automatically.
- **Immutable array updates are non-negotiable.** Using `.push()` instead of spread syntax breaks React's ability to detect state changes and trigger re-renders.
- **Controlled forms centralize input state.** Using `useState` for form data instead of uncontrolled inputs (relying on DOM state) gives React full control over validation, dynamic fields, and submission flow.
- **Dynamic object keys enable reusable handlers.** `[e.target.name]: e.target.value` allows one `handleChange` function to update any field, avoiding repetitive boilerplate for each input.
- **Modal UX requires event propagation awareness.** `stopPropagation()` on modal content prevents clicks inside the modal from bubbling to the overlay and accidentally closing it.

---

## Notes

- This repository intentionally prioritizes backend correctness over frontend completeness.
- The React UI is intentionally unstyled — it exists to demonstrate full-stack integration and backend behavior, not frontend polish.
- Known gaps for future work: frontend form validation, React component tests, and token-expiry-aware redirect after silent refresh.

---

## License

MIT
