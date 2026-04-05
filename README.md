# AAOF v2.0 Strands

> AI Agent Orchestrator Framework powered by Strands Agents SDK

---

## What is AAOF v2.0 and why does it exist?

**AAOF** (Agnostic Agent Orchestrator Framework) is a system that uses an AI agent (powered by OpenAI ChatGPT) to build, test, and deploy software projects step by step.

### The problem with v1: the agent "cheating" problem

In AAOF v1, the workflow was document-based: rules were written in Markdown files, and the AI agent was *asked* to follow them and *self-validate* its own work. This led to a fundamental problem: the agent could declare "PASS" on a test without actually running it, skip mandatory steps, or produce empty files while claiming success.

**AAOF v2.0 solves this completely.** The workflow is now controlled end-to-end by Python code using the [Strands Agents SDK](https://strandsagents.com/). The agent does the work; Python *verifies* the result. The agent cannot cheat because it is Python — not the agent — that checks whether files exist, tests pass, and services respond.

```
AAOF v1:  Markdown rules → Agent reads → Agent self-validates → 🙏 hope for the best
AAOF v2:  Python orchestrator → Agent executes → Python VERIFIES → ✅ or ❌ enforced
```

---

## Prerequisites

Before you start, make sure you have the following installed on your computer:

1. **Python 3.10 or newer** — [Download here](https://www.python.org/downloads/)
2. **Docker Desktop** — [Download here](https://www.docker.com/products/docker-desktop/)
3. **An OpenAI API key** — [Get one here](https://platform.openai.com/api-keys)

---

## Quick Start (5 steps)

### Step 1 — Clone the project

```bash
git clone https://github.com/ssignori76/aaof-strands.git
cd aaof-strands
```

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Configure your API key

```bash
cp .env.example .env
```

Open `.env` in any text editor and replace `sk-your-key-here` with your real OpenAI API key:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4 — Describe your project

Open `config.yaml` and edit the `project` section:

```yaml
project:
  name: "my-todo-app"
  description: "A simple todo list app with a REST API"
```

### Step 5 — Run the orchestrator

```bash
python aaof.py
```

That's it! AAOF will guide you through the 8-step workflow automatically.

---

## config.yaml — Field by Field

This is the **only file you need to edit**. Here is what each field means:

| Field | What it does | Example values |
|---|---|---|
| `project.name` | Your project's name (used in file names and logs) | `"my-api"` |
| `project.description` | What you want to build — describe it clearly | `"REST API for a todo app"` |
| `stack.languages` | Programming languages to use | `["javascript"]`, `["python"]` |
| `stack.frameworks` | Frameworks and libraries | `["express"]`, `["fastapi"]` |
| `stack.databases` | Database systems | `["sqlite"]`, `["postgresql"]` |
| `deploy_targets` | Where to deploy | `["DOCKER"]`, `["DOCKER", "K8S"]` |
| `environment.type` | Environment type | `"lab"`, `"staging"`, `"production"` |
| `environment.tls_required` | Require HTTPS/TLS | `true` / `false` |
| `environment.secrets_strictness` | How strict about secrets | `"relaxed"`, `"strict"` |
| `model.provider` | AI provider (currently only OpenAI) | `"openai"` |
| `model.model_id` | Which ChatGPT model to use | `"gpt-4o"`, `"gpt-4o-mini"` |
| `model.max_tokens` | Maximum tokens per agent call | `4096` |
| `model.temperature` | Creativity level (0=precise, 1=creative) | `0.2` |
| `workflow.max_retries` | How many times to retry a failed step | `3` |
| `workflow.human_approval_at` | Steps requiring your manual approval | `[2]` |
| `workflow.verbose` | Show detailed output | `true` / `false` |

---

## The 8-Step Workflow

AAOF v2.0 guides your project through 8 steps. Each step has an AI agent that does the work and a **gate check** that verifies it.

```
┌─────────────────────────────────────────────────────────────────┐
│                    AAOF v2.0 — 8 Step Workflow                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STEP 0 ── Bootstrap        Checks Docker, loads config        │
│     ↓  [Gate 0: Docker running, config valid]                  │
│  STEP 1 ── Resolution       Confirms tech stack & versions     │
│     ↓  [Gate 1: versions confirmed, security profile set]      │
│  STEP 2 ── Plan             Creates the implementation plan    │
│     ↓  [Gate 2: ✋ YOUR APPROVAL REQUIRED]                      │
│  STEP 3 ── Backup           Backs up existing files            │
│     ↓  [Gate 3: backup manifest exists]                        │
│  STEP 4 ── Implement        Generates all project files        │
│     ↓  [Gate 4: output/ has files, contracts pass]             │
│  STEP 5 ── Validate         Runs ALL tests & smoke test        │
│     ↓  [Gate 5: ⭐ ANTI-CHEAT — real HTTP check, files exist]  │
│  STEP 6 ── Rollback         (only if Step 5 fails)             │
│     ↓                                                          │
│  STEP 7 ── Consolidate      Archives results, updates docs     │
│     ↓  [Gate 7: deployed_state.json updated, changelog done]   │
│                                                                 │
│  ✅ PROJECT COMPLETE                                             │
└─────────────────────────────────────────────────────────────────┘
```

### What happens at each step

| Step | Name | What the agent does | What the gate checks |
|---|---|---|---|
| 0 | Bootstrap | Loads config, checks environment | Docker installed, rules/ has .md files |
| 1 | Resolution | Confirms exact library versions, defines security profile | `VAR_CONFIRMED_VERSIONS` set, `VAR_SECURITY_PROFILE` set |
| 2 | Plan | Creates detailed implementation plan | **Your manual approval** |
| 3 | Backup | Backs up any existing project files | `backup_manifest.json` exists |
| 4 | Implement | Generates all code, Dockerfiles, configs | Files exist in `output/`, contract checks pass |
| 5 | Validate | Creates test playbook, runs tests, HTTP smoke test | Test files exist, `test_runner.sh` is executable, HTTP 200 OK |
| 6 | Rollback | Restores from backup if Step 5 failed | (only runs on failure) |
| 7 | Consolidate | Updates changelog, archives specs | `deployed_state.json` updated, `changelog.md` updated |

---

## Gate Checks — Why the Agent Can't Cheat

Every step ends with a **gate check**: a Python function that verifies the agent actually did the work. These checks are run by Python code, not by the AI agent. The agent cannot lie to them.

**Example: Step 5 Anti-Cheat Gate**

```
Gate 5 checks:
  ✅ output/test_playbook.md exists and is > 100 bytes
  ✅ output/test_results.md contains "Test ID" and "Status"
  ✅ output/test_runner.sh exists and is executable (chmod +x)
  ✅ HTTP GET http://localhost:3000/ returns 200 OK (not a default page!)
  ✅ All files cited in test_playbook.md actually exist on disk
```

If any check fails, the orchestrator **blocks progress** and retries the step (up to `max_retries` times). The agent is told exactly what failed and must fix it.

---

## What You Can Customize

You can safely edit these files without touching any Python code:

| File/Directory | What it controls | Needs Python knowledge? |
|---|---|---|
| `config.yaml` | Project settings, model, workflow | ❌ No |
| `prompts/step*.md` | What the agent does at each step | ❌ No — plain English |
| `rules/*.md` | Coding rules and standards for the agent | ❌ No — plain English |
| `specs/active/*.md` | Your project requirements/specs | ❌ No — plain English |
| `.env` | Your API key | ❌ No |
| `gates/*.py` | What is verified at each step | ✅ Yes — Python |
| `tools/*.py` | Tools available to the agent | ✅ Yes — Python |
| `workflow/*.py` | The orchestration logic | ✅ Yes — Python |

---

## Troubleshooting

### ❌ `OPENAI_API_KEY not found`

You forgot to create the `.env` file. Run:
```bash
cp .env.example .env
# Then edit .env and add your key
```

### ❌ `Docker not found` or Gate 0 fails

Make sure Docker Desktop is running. Open Docker Desktop and wait for it to show "Docker Desktop is running".

### ❌ Step fails repeatedly

Check the output in `session/step_evidence.json` — it records exactly what each gate checked and what failed.

### ⏸️ Session was interrupted

Just run `python aaof.py` again. AAOF saves its state in `session/session_state.json` and will **resume from where it stopped**.

### ❌ `Module not found` errors

Make sure you installed dependencies:
```bash
pip install -r requirements.txt
```

---

## Project Structure

```
aaof-strands/
├── aaof.py              ← Start here: python aaof.py
├── config.yaml          ← YOUR configuration (edit this!)
├── .env                 ← YOUR API key (create from .env.example)
├── requirements.txt     ← Python dependencies
│
├── prompts/             ← What the agent does at each step (editable)
├── rules/               ← Coding rules for the agent (editable)
├── specs/active/        ← Your project specs (put .md files here)
├── output/              ← Generated project files appear here
├── session/             ← Workflow state (don't edit manually)
└── backups/             ← Automatic backups before changes
```

---

## Links

- **AAOF v1** (original document-based version): https://github.com/ssignori76/Agnostic-Agent-Orchestrator-Framework
- **Strands Agents SDK**: https://strandsagents.com/
- **OpenAI API**: https://platform.openai.com/
