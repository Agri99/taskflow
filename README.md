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

* Create, edit, and delete comments
* **Soft delete** (comments are hidden, not removed immediately)
* Role-based permissions:

  * Author can edit within time window
  * Author or task owner can delete
* **Edit window enforcement** (configurable via settings)
* Deleted comments are never editable

### Query & model invariants

* All permission rules live in **QuerySets / model methods**
* Views rely on `get_queryset()` only (no duplicated permission logic)
* Clear separation between:

  * `active()` comments
  * `editable_by(user)`
  * `deletable_by(user)`

### Background maintenance

* Management command to **purge soft-deleted comments** older than N days
* Safe by default, supports dry-run
* Fully covered by tests

---

## 🧪 Testing philosophy

* Tests describe **behavior**, not implementation
* Unauthorized access returns **404**, not redirects or permission leaks
* Boundary conditions are explicitly tested:

  * Exactly at edit-window cutoff
  * Deleted-but-recent comments
  * Repeated purge runs (idempotency)

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

## ⚙️ Key settings

```python
COMMENTS_EDIT_WINDOW_MINUTES = 15
```

Controls how long after creation a comment can be edited.

---

## 🧠 Design decisions

* **404 over 403**: prevents information leakage
* **QuerySet-driven permissions**: one source of truth
* **Soft delete + background purge**: safety and auditability
* **Backend-only scope**: clarity of learning and evaluation

---

## 🚧 Roadmap (next)

* Edited badge (`edited_at`, `edited_by`)
* UI layer (templates) *after* backend is closed
* CI pipeline (GitHub Actions)

---

## 📌 Notes

This project is intentionally opinionated and strict. Some choices (like rejecting edits at the exact cutoff) are made to surface edge cases and enforce consistency.

---

## License

MIT
