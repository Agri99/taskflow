# TaskFlow

TaskFlow is a **Django backend-focused project** built to demonstrate real-world backend engineering practices: permissions enforced at the query layer, soft deletion, time-based edit rules, background cleanup jobs, and test-driven development.

This project is intentionally **backend-first** — the focus is on robust server-side architecture, not front-end polish.

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

TaskFlow now includes a **global-first RBAC system** built on top of Django’s authentication and permission framework.

### Key Concepts

**Role**
- A named collection of Django `Permission` objects  
- Examples: `Admin`, `Moderator`, `Support`, `ReadOnly`

**Membership**
- Assigns a `User` to a `Role`
- Memberships are currently **global** (apply across the entire system)

**Permission Resolution**
- Permissions are **fine-grained**, such as:
  - `comments.add_comment`
  - `comments.change_comment`
  - `comments.delete_comment`
  - `tasks.change_task`
- QuerySets and model helpers use RBAC as the **single source of truth**

This allows permissions to be changed by adjusting role mappings — **without modifying business logic code**.

---

## 🧾 Audit Logging System

TaskFlow records an **immutable audit trail** of important actions.

### What gets logged

Audit entries are created when key operations occur, such as:

- Comment soft-deleted  
- Comment edited  
- Task updated or deleted (future expansion)

### Each audit entry stores

| Field | Meaning |
|------|--------|
| actor | The user who performed the action |
| action | `create`, `edit`, or `delete` |
| target | The object being modified (Comment, Task, etc.) |
| timestamp | When the action occurred |
| payload | Small JSON diff or metadata |

Audit entries are **append-only by design** and are not meant to be edited.

### Retention Policy

Audit records may be archived or purged after a defined retention window (implementation planned). This prevents unbounded growth while preserving forensic usefulness.

---

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

---

## 📌 Notes

* This repository intentionally prioritizes backend correctness over frontend completeness.

* The UI is minimal and exists only to surface backend behavior already enforced at the model/query level.

---

## License

MIT