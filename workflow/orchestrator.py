"""Main orchestrator — drives the 8-step AAOF workflow.

The orchestrator:
1. Loads config.yaml
2. Initialises the Strands OpenAI model
3. For each step:
   a. Builds a system prompt from prompts/ + rules/
   b. Creates a Strands Agent with the appropriate tools
   c. Executes the agent
   d. Runs the Python gate check
   e. If gate passes → advances to next step
   f. If gate fails  → retries up to max_retries, then raises
4. Handles resume: if session_state.json already has step > 0, resumes there
5. Uses `rich` for formatted terminal output
"""
import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from strands import Agent
from strands.models.openai import OpenAIModel

from workflow.state import SessionState
from workflow.steps import STEPS, TOTAL_STEPS

console = Console()


def _load_config(config_path: str) -> Dict[str, Any]:
    """Load and return the YAML configuration file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"config.yaml not found at {config_path}. "
            "Make sure you are running from the project root directory."
        )
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _load_prompt(filename: str) -> str:
    """Load a markdown system prompt from the prompts/ directory."""
    path = Path("prompts") / filename
    if not path.exists():
        return f"[System prompt not found: {filename}]"
    return path.read_text(encoding="utf-8")


def _load_rules(filenames: List[str]) -> str:
    """Concatenate rule files into a single rules block."""
    parts: List[str] = []
    for fn in filenames:
        rpath = Path("rules") / fn
        if rpath.exists():
            parts.append(f"## {rpath.stem}\n\n{rpath.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(parts)


def _build_system_prompt(prompt_file: str, rules_files: List[str], config: Dict[str, Any]) -> str:
    """Compose the full system prompt for an agent step."""
    step_prompt = _load_prompt(prompt_file)
    rules_block = _load_rules(rules_files)
    project_ctx = (
        f"## Project Context\n\n"
        f"- Name: {config.get('project', {}).get('name', 'unknown')}\n"
        f"- Description: {config.get('project', {}).get('description', '')}\n"
        f"- Stack: {config.get('stack', {})}\n"
        f"- Deploy targets: {config.get('deploy_targets', [])}\n"
    )
    return f"{step_prompt}\n\n---\n\n{project_ctx}\n\n---\n\n{rules_block}"


class Orchestrator:
    """Main workflow orchestrator.

    Attributes:
        config_path: Path to config.yaml.
        config:      Loaded configuration dict.
        state:       SessionState instance.
    """

    def __init__(self, config_path: str = "config.yaml") -> None:
        self.config = _load_config(config_path)
        self.state = SessionState()
        self._model = OpenAIModel(
            client_args={"api_key": os.getenv("OPENAI_API_KEY")},
            model_id=self.config.get("model", {}).get("model_id", "gpt-4o"),
            params={
                "max_tokens": self.config.get("model", {}).get("max_tokens", 4096),
                "temperature": self.config.get("model", {}).get("temperature", 0.2),
            },
        )
        self._max_retries: int = self.config.get("workflow", {}).get("max_retries", 3)
        self._human_approval_at: List[int] = self.config.get(
            "workflow", {}
        ).get("human_approval_at", [2])
        self._verbose: bool = self.config.get("workflow", {}).get("verbose", True)

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Execute or resume the workflow."""
        start_step = self.state.step
        project_name = self.config.get("project", {}).get("name", "project")

        console.print(
            Panel.fit(
                f"[bold cyan]AAOF v2.0 Strands[/bold cyan]\n"
                f"Project: [green]{project_name}[/green]\n"
                f"Resuming from step: [yellow]{start_step}[/yellow]",
                title="🚀 Starting",
            )
        )

        for step_num in range(start_step, TOTAL_STEPS):
            step_def = STEPS.get(step_num)
            if step_def is None:
                continue

            success = self._run_step_with_retry(step_num, step_def)
            if not success:
                console.print(
                    f"[bold red]❌ Step {step_num} ({step_def.name}) failed after "
                    f"{self._max_retries} retries. Aborting.[/bold red]"
                )
                raise RuntimeError(
                    f"Step {step_num} ({step_def.name}) could not complete successfully."
                )

            # Skip Step 6 (Rollback) if we're not in a failure scenario
            if step_num == 4:
                # After Implement, go directly to Validate (skip Rollback path)
                pass

        console.print(
            Panel.fit(
                "[bold green]✅ Workflow complete![/bold green]\n"
                "Check output/ for generated files.",
                title="🎉 Done",
            )
        )

    # ------------------------------------------------------------------
    # Step execution helpers
    # ------------------------------------------------------------------

    def _run_step_with_retry(self, step_num: int, step_def: Any) -> bool:
        """Run a step, retrying up to max_retries times if the gate fails.

        Returns True if the step ultimately passed, False otherwise.
        """
        for attempt in range(1, self._max_retries + 1):
            console.print(
                f"\n[bold blue]▶ Step {step_num} — {step_def.name}[/bold blue] "
                f"(attempt {attempt}/{self._max_retries})"
            )

            # Human approval gate (before running the agent)
            if step_num in self._human_approval_at or step_def.requires_human_approval:
                if not self._request_human_approval(step_num, step_def.name):
                    console.print("[yellow]⏸️  User declined. Stopping.[/yellow]")
                    return False
                self.state.set("VAR_HUMAN_APPROVAL_STEP2", True)

            # Execute the agent
            self._execute_agent(step_num, step_def)

            # Run the gate check
            gate_passed, gate_results = self._run_gate(step_num, step_def)

            # Log evidence
            self.state.record_evidence(step_num, step_num + 1, gate_results)

            # Display gate results
            self._display_gate_results(step_num, step_def.name, gate_results, gate_passed)

            if gate_passed:
                self.state.advance_step(step_num + 1)
                return True

            if attempt < self._max_retries:
                console.print(
                    f"[yellow]⚠️  Gate failed. Retrying step {step_num}…[/yellow]"
                )

        return False

    def _execute_agent(self, step_num: int, step_def: Any) -> str:
        """Build and invoke the Strands Agent for a step."""
        system_prompt = _build_system_prompt(
            step_def.prompt_file, step_def.rules_files, self.config
        )

        agent = Agent(
            model=self._model,
            system_prompt=system_prompt,
            tools=step_def.tools,
        )

        task_prompt = self._build_task_prompt(step_num, step_def)

        if self._verbose:
            console.print(f"[dim]  🤖 Invoking agent for Step {step_num} ({step_def.name})…[/dim]")

        result = agent(task_prompt)
        return str(result)

    def _run_gate(self, step_num: int, step_def: Any):
        """Instantiate and evaluate the gate for this step."""
        gate = step_def.gate(config=self.config, state=self.state)
        return gate.evaluate()

    def _build_task_prompt(self, step_num: int, step_def: Any) -> str:
        """Compose the per-step task instruction sent to the agent."""
        project = self.config.get("project", {})
        return (
            f"Execute STEP {step_num} — {step_def.name.upper()}.\n\n"
            f"Project name: {project.get('name', 'unknown')}\n"
            f"Description: {project.get('description', '')}\n\n"
            f"Current session step: {self.state.step}\n"
            f"Your task is defined in the system prompt above. "
            f"Produce all required artefacts now. "
            f"Remember: you do NOT decide if this step is complete — "
            f"a Python gate check verifies your work automatically."
        )

    def _request_human_approval(self, step_num: int, step_name: str) -> bool:
        """Pause execution and ask the user for approval to continue."""
        console.print(
            Panel(
                f"[bold yellow]✋ Human approval required[/bold yellow]\n\n"
                f"Step {step_num} ({step_name}) requires your review.\n"
                f"Please inspect the generated plan in the output/ directory.\n\n"
                f"Type [green]yes[/green] to continue, or anything else to stop.",
                title="👤 Your Input Required",
            )
        )
        answer = input("Continue? (yes/no): ").strip().lower()
        return answer in {"yes", "y"}

    def _display_gate_results(
        self, step_num: int, step_name: str, results: List[Any], passed: bool
    ) -> None:
        """Render gate results in a Rich table."""
        table = Table(title=f"Gate {step_num} — {step_name}", show_header=True)
        table.add_column("Check ID", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Message")

        for r in results:
            status = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
            table.add_row(r.gate_id, status, r.message)

        console.print(table)
        overall = "[bold green]✅ GATE PASSED[/bold green]" if passed else "[bold red]❌ GATE FAILED[/bold red]"
        console.print(overall)
