# Security Rules

These rules apply to all generated code and configuration. They are verified by the gate checks and are non-negotiable.

## Secrets Management

- **NEVER** hardcode API keys, passwords, tokens, or any secrets in source code.
- All secrets MUST be loaded from environment variables.
- Every project MUST have a `.env.example` file documenting required variables.
- The actual `.env` file MUST be in `.gitignore`.
- Use `os.environ.get("KEY")` or equivalent — never string literals.

## Container Security

- Docker containers MUST run as a **non-root user**.
- Add to every Dockerfile:
  ```dockerfile
  RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
  USER appuser
  ```
- Do NOT use `USER root` in production images.
- Pin base image versions (e.g., `node:20.11-alpine3.19` not `node:latest`).

## Input Validation

- Validate and sanitise ALL user input before using it.
- Use parameterised queries for all database operations — never string concatenation.
- Return generic error messages to clients; log details server-side.

## Dependencies

- Pin all dependency versions in package files (e.g., `"express": "4.18.2"` not `"^4"`).
- Check for known CVEs before using a new dependency.

## Access Control

- Follow the principle of least privilege.
- Do not expose internal ports beyond what is required.
- In production environments (`environment.type: "production"`), TLS is mandatory.

## File Permissions

- Shell scripts: `chmod +x` only for scripts that need to be executed.
- Configuration files: readable only by the application user.
- Log files: writable only by the application user.
