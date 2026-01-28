# TaskFlow

TaskFlow is a **Django backend-focused project** built to demonstrate real-world backend engineering practices: permissions enforced at the query layer, soft deletion, time-based edit rules, background cleanup jobs, and test-driven development.

This project is intentionally **backend-first**. There is no frontend UI yet; all behavior is exercised and proven through unit tests and Django views.

---

## 🎯 Project goals

* Practice writing **production-style Django code**, not tutorial snippets
* Enforce permissions at the **model/queryset level** (not scattered in views)
* Avoid "vibe coding" by using **tests to drive behavior**
* Build a portfolio-ready backend project that can later support a UI or API

---

## ✅ Implemented features

### Tasks

* Task ownership model
* Task-detail access control via `get_queryset`

### Comments
- Create, edit, and delete comments
- **Soft delete** (comments are hidden, not removed immediately)
- Role-based permissions:
  - Authors can edit **within a configurable edit window**
  - Authors or task owners can delete
- **FIRST_EDIT_ONLY**: the first successful edit sets `edited_at`; future edits do not overwrite it
- Edited comments display an **“(edited)” badge** in the UI (derived from `edited_at`)
- Deleted comments are never editable or shown in normal task views

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

---

## 🧠 Query & Model Design

All permission rules live in **QuerySets and model methods**.

### QuerySet helpers

- `CommentQuerySet.active()` → visible (non-deleted) comments  
- `CommentQuerySet.editable_by(user)` → comments editable by a user  
- `CommentQuerySet.deletable_by(user)` → comments deletable by a user  

### Model helpers

- `Comment.can_be_edited_by(user)`  
- `Comment.can_be_deleted_by(user)`  
- `Comment.mark_edited()` → sets `edited_at` once  
- `Comment.is_edited` → derived property (True if `edited_at` exists)

Views **only** rely on these helpers — no duplicated logic.

---

## 🧪 Testing Philosophy

- Tests describe **behavior**, not implementation details  
- Boundary conditions are explicitly tested:
  - Exact edit-window cutoff
  - Attempted edits after deletion
  - Re-edit attempts not overwriting `edited_at`
- Unauthorized access returns **404** to prevent information leakage

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

## 🧠 Design decisions

* **404 over 403**: Prevents information leakage
* **QuerySet-driven permissions**: One source of truth
* **Soft delete + background purge**: Safety and auditability
* **FIRST_EDIT_ONLY edit tracking**: Preserves original edit timestamp
* **Backend-first scope**: Clarity of learning and evaluation

---

## 🚧 Roadmap (next)

* Production-ready Django settings
* Static/media handling
* Deployment configuration

---

## 📌 Notes

This project intentionally prioritizes backend correctness over frontend complexity.
The UI is minimal and exists only to surface backend behavior already enforced at the model/query level.

---

## License

MIT