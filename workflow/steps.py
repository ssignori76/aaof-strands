"""Step definitions — maps step numbers to their configuration."""
from dataclasses import dataclass, field
from typing import List, Type

from gates.base import BaseGate
from gates.gate_step0 import GateStep0
from gates.gate_step1 import GateStep1
from gates.gate_step2 import GateStep2
from gates.gate_step3 import GateStep3
from gates.gate_step4 import GateStep4
from gates.gate_step5 import GateStep5
from gates.gate_step6 import GateStep6
from gates.gate_step7 import GateStep7

from tools.docker_tools import docker_build, docker_compose_up, docker_compose_down, docker_health_check
from tools.file_tools import read_file, write_file, list_directory, check_file_exists, append_to_file
from tools.shell_tools import run_command
from tools.k8s_tools import kubectl_apply, kubectl_get_pods, kubectl_logs, kubectl_delete
from tools.test_tools import smoke_test, run_test_script


@dataclass
class StepDef:
    """Definition of a single workflow step."""

    name: str
    prompt_file: str                      # filename inside prompts/
    rules_files: List[str]                # filenames inside rules/
    tools: List                           # @tool callables available to the agent
    gate: Type[BaseGate]                  # Gate class to run after the step
    requires_human_approval: bool = False  # True if step needs user confirmation


# ---------------------------------------------------------------------------
# Central step registry
# ---------------------------------------------------------------------------

STEPS = {
    0: StepDef(
        name="Bootstrap",
        prompt_file="step0_bootstrap.md",
        rules_files=["docker_rules.md", "development_rules.md"],
        tools=[run_command, check_file_exists, list_directory],
        gate=GateStep0,
    ),
    1: StepDef(
        name="Resolution",
        prompt_file="step1_resolution.md",
        rules_files=["security_rules.md", "development_rules.md"],
        tools=[run_command, read_file, write_file],
        gate=GateStep1,
    ),
    2: StepDef(
        name="Plan",
        prompt_file="step2_plan.md",
        rules_files=["development_rules.md", "testing_rules.md"],
        tools=[read_file, write_file, list_directory],
        gate=GateStep2,
        requires_human_approval=True,
    ),
    3: StepDef(
        name="Backup",
        prompt_file="step3_backup.md",
        rules_files=["development_rules.md"],
        tools=[read_file, write_file, list_directory, run_command],
        gate=GateStep3,
    ),
    4: StepDef(
        name="Implement",
        prompt_file="step4_implement.md",
        rules_files=["development_rules.md", "security_rules.md", "docker_rules.md"],
        tools=[
            read_file, write_file, list_directory, append_to_file,
            run_command, docker_build, docker_compose_up,
        ],
        gate=GateStep4,
    ),
    5: StepDef(
        name="Validate",
        prompt_file="step5_validate.md",
        rules_files=["testing_rules.md", "security_rules.md"],
        tools=[
            read_file, write_file, run_command,
            smoke_test, run_test_script,
            docker_health_check, docker_compose_up, docker_compose_down,
        ],
        gate=GateStep5,
    ),
    6: StepDef(
        name="Rollback",
        prompt_file="step6_rollback.md",
        rules_files=["error_handling_rules.md"],
        tools=[read_file, write_file, run_command, docker_compose_down],
        gate=GateStep6,  # Dedicated rollback gate checks report and restored files
    ),
    7: StepDef(
        name="Consolidate",
        prompt_file="step7_consolidate.md",
        rules_files=["development_rules.md"],
        tools=[read_file, write_file, list_directory, run_command],
        gate=GateStep7,
    ),
}

TOTAL_STEPS = len(STEPS)
