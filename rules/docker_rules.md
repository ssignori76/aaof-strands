# Docker Rules

All containerisation must follow these rules.

## Container-First Principle

Every project MUST be runnable with a single command:

```bash
docker compose up -d
```

No exceptions. The application must start, initialise its database, and be ready to serve requests within 60 seconds.

## Dockerfile Best Practices

1. **Use official base images** — prefer `-alpine` variants for smaller size.
2. **Pin versions** — `FROM node:20.11-alpine3.19` not `FROM node:latest`.
3. **Use multi-stage builds** for compiled languages to keep the final image small.
4. **Minimise layers** — combine related RUN commands with `&&`.
5. **Non-root user** — always create and switch to a non-root user (see security_rules.md).
6. **Copy only what's needed** — use `.dockerignore` to exclude development files.
7. **Set WORKDIR** explicitly (e.g., `WORKDIR /app`).
8. **Expose ports** explicitly with the `EXPOSE` instruction.

## docker-compose.yml Best Practices

1. **Health checks** — define a `healthcheck` for every service.
2. **Restart policy** — use `restart: unless-stopped` for services.
3. **Named volumes** — use named volumes for persistent data (not bind mounts in production).
4. **Environment variables** — load from `.env` file, never inline secrets.
5. **Networks** — define explicit networks; do not rely on the default network.
6. **Depends_on with condition** — use `condition: service_healthy` for startup ordering.

## Example healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

## Required Files

Every project containerisation MUST include:
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
