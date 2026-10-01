---
type: llm
weight: 2
focus: { source: file, path: generated-docs/DATABASE.md }
---

Ground truth (Flask-SQLAlchemy models in app/models.py; Alembic via Flask-Migrate; 9 migration files in migrations/versions):
- Tables: user, post, message, notification, task, and the association table followers.
- Foreign keys, all referencing user.id: post.user_id; message.sender_id; message.recipient_id; notification.user_id; task.user_id; followers.follower_id; followers.followed_id.
- user has password_hash and token columns (sensitive).

PASS if the ER diagram and text cover these tables, draw only the foreign keys listed above as real relationships (anything else labelled logical or not enforced), describe followers as a many-to-many self-relationship of user, explain the Flask-Migrate/Alembic workflow, and mark password_hash or token as sensitive.
FAIL if it invents tables or columns, draws a relationship that is not in the list as a real foreign key, omits followers, or shows real-looking secret values.
