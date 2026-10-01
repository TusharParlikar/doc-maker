---
type: llm
focus: last_message
---

PASS if the answer explains that protected routes use JWT bearer tokens verified with JWT_SECRET in middleware/auth.js, that /me is protected and /public is not, and that invalid tokens get a 401.
FAIL if it is wrong about these points or writes documentation files instead of answering.
