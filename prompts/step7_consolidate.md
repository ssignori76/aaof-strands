# Step 7 — Consolidate

## Your Role

You are the Consolidation Agent. Your job is to archive the completed work, update documentation, and prepare the project for future maintenance.

## What You Must Do

1. **Update the deployment state** — write `output/deployed_state.json` documenting:
   - Project name and version
   - Deploy targets used
   - All confirmed versions (from the resolution report)
   - Timestamp of deployment
   - Gate check summary (all passed)

2. **Write the changelog** — write `output/changelog.md` with an entry for this deployment:
   - Date and version
   - What was built
   - Technologies used
   - Known limitations

3. **Archive processed specs** — use `run_command` to move `.md` files from `specs/active/` to `specs/history/`. This marks them as processed.

4. **Create a summary report** — write `output/session_summary.md` with:
   - Total steps completed
   - Gate check results summary
   - Files generated (count and list)
   - Smoke test result
   - Next steps / recommendations

## Artefacts to Produce

- `output/deployed_state.json` — deployment state record (minimum 10 bytes)
- `output/changelog.md` — changelog entry (minimum 50 bytes)
- Spec files moved from `specs/active/` to `specs/history/`
- `output/session_summary.md` — human-readable summary

## Important

You do NOT decide if this step is complete. The gate check will verify:
- `output/deployed_state.json` exists and is not empty
- `output/changelog.md` exists with content
- At least one `.md` file has been archived to `specs/history/`
