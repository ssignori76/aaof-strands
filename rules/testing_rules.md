# Testing Rules

All testing must follow these rules. These are enforced by the Step 5 gate check — you cannot fake compliance.

## Categories of Tests Required

Every project must include tests in these categories:

| Category | Minimum Count | Description |
|---|---|---|
| Unit tests | `max(5, LOC / 100)` | Test individual functions in isolation |
| Integration tests | 3 | Test interactions between components (e.g., API → database) |
| Smoke tests | 1 | HTTP GET to the running application — must return 200 |
| Security tests | 2 | Check for no hardcoded secrets, non-root container |
| Contract tests | 1 per endpoint | Verify each API endpoint matches its contract |

**Minimum test count formula:** `max(5, lines_of_code / 100) + 3 + 1 + 2 + endpoints`

## Test-Driven Approach

1. Write the test plan BEFORE writing test scripts.
2. The test runner script must exit with code 0 if all tests pass, non-zero otherwise.
3. All tests must produce output that can be read by a human in `test_results.md`.

## Test Results Format

`output/test_results.md` MUST contain the following column headers:

```
| Test ID | Name | Status | Duration | Notes |
```

Every executed test must appear as a row. Status must be `PASS` or `FAIL`.

## Smoke Test Rules

- Must use real HTTP — `requests.get("http://localhost:3000/")`.
- Must reject default pages (nginx, Apache "It works!", etc.).
- Must verify the actual application response.
- Port 3000 is the default — adjust for your stack.

## What Is NOT Allowed

- Marking a test as PASS without running it.
- Creating `test_results.md` without executing `test_runner.sh`.
- Declaring the smoke test passed without a real HTTP response.
- Tests that only check whether files exist (unless that IS the test).
