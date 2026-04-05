# Development Rules

These rules apply to all generated source code files.

## File Headers

Every source code file MUST start with a header comment:

```
# filename: path/to/file.ext
# purpose: One sentence describing this file's responsibility
# created: YYYY-MM-DD
```

## File Size Limit

**No single file may exceed 200 lines of code.**

If a file exceeds this limit:
- Split it into multiple modules with clear responsibilities.
- Create an `__init__.py` (Python) or `index.js` (Node.js) to re-export.

## Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Python files | `snake_case.py` | `user_service.py` |
| JavaScript files | `camelCase.js` or `kebab-case.js` | `userService.js` |
| Classes | `PascalCase` | `UserService` |
| Functions/methods | `snake_case` (Python), `camelCase` (JS) | `get_user`, `getUser` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| Database tables | `snake_case` plural | `user_sessions` |

## Type Hints (Python)

All Python functions MUST have type hints:

```python
def get_user(user_id: int) -> dict:
    ...
```

## Documentation

- Public functions and classes must have docstrings.
- Use Google-style docstrings (Args/Returns/Raises sections).

## Error Handling

- Never use bare `except:` — always catch specific exceptions.
- Log errors with context (which file, which function, what was attempted).
- Return meaningful error messages.
- See `error_handling_rules.md` for details.

## Code Quality

- No commented-out code in committed files.
- No `TODO` comments that block functionality — resolve them before completing the step.
- No `print()` statements used for debugging — use proper logging.
