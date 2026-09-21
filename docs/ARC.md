# ARC-Easy (TED-24)

Allen Institute ARC-Easy, CC BY-SA 4.0. Study **2251** train facts. Exam **570** validation items. The solver does **not** see `answerKey` until scoring.

Rule: one studied fact shares ≥2 stem words and matches exactly one choice → that letter. Else **leftover** (no guess).

| | n |
|--|--:|
| answered | 70 |
| correct | 48 |
| wrong | 22 |
| leftover | 500 |
| precision when answered | 68.6% |
| accuracy if leftover counts as miss | 8.4% |

Not an LLM. Science facts we have not studied stay leftover.
