"""Session state manager — the single source of truth for workflow state."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class SessionState:
    """Manages session/session_state.json — the ONLY source of truth for
    workflow state.

    All step transitions, variable values, and gate results are persisted
    here so that sessions can be safely resumed after an interruption.
    """

    STATE_FILE = Path("session/session_state.json")
    EVIDENCE_FILE = Path("session/step_evidence.json")

    DEFAULTS: Dict[str, Any] = {
        "VAR_SESSION_STEP": 0,
        "VAR_DOCKER_INSTALLED": False,
        "VAR_SOURCE_OF_TRUTH": "",
        "VAR_CONFIRMED_VERSIONS": {},
        "VAR_SECURITY_PROFILE": "",
        "VAR_DEPLOY_TARGET": [],
        "VAR_ACTIVE_BACKUP_PATH": "",
        "VAR_VALIDATION_RESULT": "",
        "VAR_REGRESSION_CHECK": "",
        "VAR_CONTRACT_CHECK": "",
        "VAR_RETRY_COUNT": 0,
        "VAR_HUMAN_APPROVAL_STEP2": False,
    }

    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}
        self.load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load state from disk, or initialise with defaults."""
        if self.STATE_FILE.exists():
            self._data = json.loads(self.STATE_FILE.read_text(encoding="utf-8"))
        else:
            self._data = dict(self.DEFAULTS)
            self.save()

    def save(self) -> None:
        """Write current state to disk atomically."""
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._data["_last_updated"] = datetime.now(timezone.utc).isoformat()
        self.STATE_FILE.write_text(
            json.dumps(self._data, indent=2), encoding="utf-8"
        )

    # ------------------------------------------------------------------
    # Step management
    # ------------------------------------------------------------------

    @property
    def step(self) -> int:
        """Current step number."""
        return int(self._data.get("VAR_SESSION_STEP", 0))

    def advance_step(self, to_step: int) -> None:
        """Advance the workflow to *to_step* and persist."""
        self._data["VAR_SESSION_STEP"] = to_step
        self.save()

    # ------------------------------------------------------------------
    # Generic variable access
    # ------------------------------------------------------------------

    def set(self, key: str, value: Any) -> None:
        """Set a workflow variable and persist immediately."""
        self._data[key] = value
        self.save()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a workflow variable by key."""
        return self._data.get(key, default)

    # ------------------------------------------------------------------
    # Evidence logging
    # ------------------------------------------------------------------

    def record_evidence(
        self, from_step: int, to_step: int, results: List[Any]
    ) -> None:
        """Append a gate-result record to step_evidence.json.

        Args:
            from_step: The step that was just completed.
            to_step:   The step we are advancing to.
            results:   List of GateResult objects from the gate check.
        """
        evidence: Dict[str, Any] = {"step_transitions": []}
        if self.EVIDENCE_FILE.exists():
            evidence = json.loads(
                self.EVIDENCE_FILE.read_text(encoding="utf-8")
            )

        evidence["step_transitions"].append(
            {
                "from": from_step,
                "to": to_step,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "gate_results": [
                    {
                        "id": r.gate_id,
                        "passed": r.passed,
                        "message": r.message,
                    }
                    for r in results
                ],
                "gate_result": "PASS" if all(r.passed for r in results) else "FAIL",
            }
        )

        self.EVIDENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.EVIDENCE_FILE.write_text(
            json.dumps(evidence, indent=2), encoding="utf-8"
        )
