# Error Handling Rules

All code must handle errors gracefully and informatively.

## Retry Logic

Operations that interact with external systems (databases, HTTP APIs, Docker) MUST implement retry logic:

- **Maximum retries:** 3 (configurable)
- **Backoff:** exponential with jitter — wait `2^attempt + random(0, 1)` seconds
- **Retriable errors:** network timeouts, temporary service unavailability (5xx)
- **Non-retriable errors:** validation errors (4xx), authentication errors (401/403)

## Logging Standards

Every significant operation must be logged at the appropriate level:

| Level | When to Use | Example |
|---|---|---|
| `DEBUG` | Detailed flow information | "Checking Docker version..." |
| `INFO` | Normal operations | "Step 3 completed: backup created at backups/2024-01-15/" |
| `WARNING` | Recoverable issues | "Docker health check returned 'starting', retrying..." |
| `ERROR` | Failures that halt a step | "Gate 5 FAILED: smoke test returned 404" |
| `CRITICAL` | Unrecoverable failures | "Fatal error: config.yaml not found" |

## Error Messages

Good error messages answer three questions:
1. **What** happened? (the error)
2. **Where** did it happen? (file, function, step)
3. **What to do** about it? (actionable hint)

Example:
```
❌ Gate 5 FAILED: SMOKE_TEST — Connection refused (http://localhost:3000/)
   → The application is not running. Check: docker compose logs app
```

## Exception Handling Pattern

```python
try:
    result = some_operation()
except SpecificException as exc:
    logger.error("Context: %s — Error: %s", context, exc)
    raise OperationError(f"Failed to do X: {exc}") from exc
finally:
    cleanup_if_needed()
```

## What Is NOT Allowed

- Swallowing exceptions silently (`except: pass`).
- Logging an error and then continuing as if it did not happen.
- Retrying non-retriable errors (e.g., retrying a 401 Unauthorized).
- Stack traces in user-facing output (log them, show a friendly message).
