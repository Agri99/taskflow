# TaskFlow

TaskFlow is a **Django backend-focused project** built to demonstrate real-world backend engineering practices: permissions enforced at the query layer, soft deletion, time-based edit rules, background cleanup jobs, and test-driven development.

This project is intentionally **backend-first** — the focus is on robust server-side architecture, not front-end polish.

This is designed as an internal tool where admins provision accounts. For public-facing deployment, a registration system would be added.

---

## 🎯 Project goals

- Write **production-style Django code**, not tutorial snippets  
- Enforce permissions at the **model / queryset layer** (single source of truth)  
- Use **tests to drive behavior** and protect invariants  
- Provide a portfolio-ready backend blueprint that can later support a UI or API
- Implement **RBAC (Role-Based Access Control)** with proper permission mapping  
- Maintain an **immutable audit trail** of critical actions

---

## 🔐 Permissions Overview

| Action | Comment Author | Task Owner | Other Users |
|--------|----------------|------------|-------------|
| Create comment | ✅ | ✅ | ❌ |
| Edit comment (within window) | ✅ | ❌ | ❌ |
| Delete comment | ✅ | ✅ | ❌ |

Additional rules:
- Deleted comments cannot be edited or deleted again  
- Edited state is derived from `edited_at` (no duplicated boolean field)  
- UI visibility is driven by flags computed in views, not templates  

> These business rules are now enforced through a **Role-Based Access Control system** described below.

---

## 🛡️ RBAC (Role-Based Access Control)

TaskFlow implements a production-grade RBAC system that separates business rules from administrative permissions.

## 🛡️ RBAC (Role-Based Access Control)

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

✅ **Flexible role assignment** - Change permissions without code changes
✅ **Single source of truth** - Permissions checked in model layer
✅ **Organization-scoped** - Each org has isolated data
✅ **Superuser override** - Admins can access cross-org audit logs
✅ **Integration with business rules** - RBAC supplements, doesn't replace, ownership logic

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
- `comments.delete_comment` - Remove inappropriate comments
- `rbac.view_auditentry` - Monitor user actions

**Auditor:**
- `rbac.view_auditentry` - Read-only access to audit logs

**Content Manager:**
- `tasks.add_task`
- `tasks.change_task`
- `tasks.delete_task`
- `comments.delete_comment`

### Testing RBAC

Run the integration test:
```bash
pytest rbac/tests/test_rbac_integration.py -v
```

Or test manually:
1. Create a moderator role with delete permissions
2. Assign role to a test user
3. Log in as that user
4. Delete another user's comment - should succeed
5. Check audit log - entry should show the deletion

---

## 🧾 Audit Logging System

TaskFlow records an **immutable audit trail** of all critical actions.

### What Gets Logged

Audit entries are automatically created for:
- ✅ Comment created (`Comment.create_with_audit()`)
- ✅ Comment edited (`comment.apply_edit()`)
- ✅ Comment deleted (`comment.soft_delete()`)

Future: Task updates, role changes, membership changes

### Audit Entry Structure

| Field | Description |
|-------|-------------|
| `actor` | User who performed the action (null for system actions) |
| `action` | One of: `create`, `edit`, `delete` |
| `target` | The object that was modified (GenericForeignKey) |
| `timestamp` | When the action occurred (indexed) |
| `payload` | JSON metadata (e.g., `{"old": "...", "new": "..."}`) |
| `organization` | Organization scope (for data isolation) |

### Viewing Audit Logs

**Option 1: Django Admin (Read-Only)**
```
/admin/rbac/auditentry/
```
- Filter by action, date, target type, organization
- Search by username or payload content
- Immutable (cannot edit or delete entries)

**Option 2: Custom Audit Viewer**
```
/rbac/audit/
```
- User-friendly interface with advanced filtering
- Requires `rbac.view_auditentry` permission
- Organization-scoped (users only see their org's logs)
- Superusers see all logs across all organizations

**Filtering options:**
- By action type (create/edit/delete)
- By actor (which user performed the action)
- By target type (comment/task/etc.)
- Text search in payload or usernames
- Paginated (50 entries per page)

### Security & Immutability

**Design principles:**
- Audit entries use `editable=False` in admin
- No `add_auditentry` or `change_auditentry` permissions granted to any role
- `delete_auditentry` disabled for all users
- Append-only by design

**Enforcement:**
- Django admin configured with `has_add_permission = False`
- Django admin configured with `has_delete_permission = False`
- Template fields set to `readonly_fields` for all columns

### Retention Policy

**Current:** Audit logs are retained indefinitely

**Future consideration:** Implement archival/purge policy
- Archive logs older than X months to cold storage
- Purge logs older than Y years (with legal compliance review)
- Maintain forensic usefulness while preventing unbounded growth

## 🚩 Project highlights

- Task model with ownership and secure `TaskDetailView` access  
- Comment system with:
  - Create / edit / soft-delete behavior
  - **Edit window** enforcement (`COMMENTS_EDIT_WINDOW_MINUTES`)
  - **FIRST_EDIT_ONLY** semantics — `edited_at` set once on first successful edit
  - `(edited)` badge derived from `edited_at` (no boolean duplication)
- Permission design:
  - Model & QuerySet-driven helpers (`editable_by`, `deletable_by`, `can_be_*`)
  - Views use `get_queryset()` and view-level flags for presentation
- Background maintenance:
  - `purge_comments` management command to permanently delete old soft-deleted records (supports `--dry-run`)
- Developer experience:
  - Dockerized dev environment (Postgres) with Docker Compose
  - CI: GitHub Actions runs tests on push/PR
  - Tests use `pytest` / `pytest-django` and cover edge cases

---

## 🧠 Architecture & tech stack

- **Framework:** Django  
- **Database (dev/prod parity):** PostgreSQL (Docker), SQLite used for local dev/test if configured that way  
- **Testing:** pytest + pytest-django, Django test client  
- **DevOps:** Docker, Docker Compose, GitHub Actions (CI)
- **RBAC:** Django `Permission` model + custom Role & Membership layer  
- **Audit:** GenericForeignKey-based immutable audit log  

- **Design principles:**
  - Single source of truth for permissions (QuerySets + Model methods)
  - Templates remain presentation-only; business rules live on the server
  - Fail-safe defaults: soft delete + purge, 404 over 403 to avoid leaking presence

---

## Security Architecture

- Role-based access control (RBAC)
- Model-level permission enforcement
- Queryset-level filtering
- Audit logging for create/edit/delete
- Permission-gated audit visibility

---

## 🧪 Testing Philosophy

- Tests describe **behavior**, not implementation details  
- Boundary conditions are explicitly tested:
  - Exact edit-window cutoff
  - Attempted edits after deletion
  - Re-edit attempts not overwriting `edited_at`
- Unauthorized access returns **404** to prevent information leakage
- RBAC permission matrices will be tested to ensure correct role enforcement
- Audit tests ensure critical actions create immutable audit entries

Run tests with:

```bash
python manage.py test
```

---


## 🧹 Background purge command

Permanently delete soft-deleted comments older than a given number of days.

Dry run (recommended):

```bash
python manage.py purge_comments --days 30 --dry-run
```

Actual deletion:

```bash
python manage.py purge_comments --days 30
```

---

## 🐳 Running with Docker

TaskFlow can be run fully inside Docker with PostgreSQL.

* Copy the example file and adjust values if needed:

'''bash
cp .env.example .env
'''

* Build containers:

'''bash
docker compose build
'''

* Start the application:

'''bash
docker compose up
'''

The app will be available at:

'''bash
http://localhost:8000/
'''

* Run test inside Docker

'''bash
docker compose run --rm web python manage.py test
'''

* Stop containers

'''bash
docker compose down
'''

---

## ⚙️ Key settings

```python
COMMENTS_EDIT_WINDOW_MINUTES = 15
```

Controls how long after creation a comment can be edited.

---

## 🧾 Lessons learned

* **Model-driven rules scale better than view-driven checks.** Putting permissions in QuerySets prevents duplication and accidental leaks.

* **Derived state is preferable to duplicate flags.** edited_at as the source of “edited” avoids drift and keeps tests simple.

* **Tests catch integration surprises early.** Moving to an environment-based settings layout revealed template path and redirect assumptions that were otherwise hidden.

* **Containerized dev + CI = reproducible engineering.** Docker + GitHub Actions ensured the same tests run in dev and CI, surfacing env-specific issues quickly.

* **Incremental, opinionated changes win.** Small, well-tested changes (UI-only or model-only) are safer than broad refactors.

* **RBAC** centralizes authorization logic and reduces permission drift

* **Audit trails** are essential for production-grade systems

* **RBAC centralizes authorization** - Roles can be modified without touching code, making permission management scalable

* **Audit trails require immutability** - Admin interfaces must be carefully configured to prevent tampering with historical records

* **Template logic should trust the backend** - Permission checks belong in models/views, not templates. The template should display what the view decides, not make authorization decisions itself

* **Organization scoping is a cross-cutting concern** - QuerySet helpers that apply organization filtering consistently prevent data leakage and simplify security

* **Superuser access requires special handling** - Production systems need privileged accounts that can operate across organizational boundaries for support and debugging

---

## 📌 Notes

* This repository intentionally prioritizes backend correctness over frontend completeness.

* The UI is minimal and exists only to surface backend behavior already enforced at the model/query level.

---

## License

MIT