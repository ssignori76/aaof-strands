"""Gate Step 3 — Backup: verify a backup manifest was created."""
from pathlib import Path
from typing import List

from gates.base import BaseGate, GateResult


class GateStep3(BaseGate):
    """Gate checks for Step 3 (Backup)."""

    def check_all(self) -> List[GateResult]:
        backup_path = self.state.get("VAR_ACTIVE_BACKUP_PATH", "")
        if not backup_path:
            return [
                GateResult(
                    "BACKUP_PATH",
                    False,
                    "❌ VAR_ACTIVE_BACKUP_PATH not set — agent must create a backup",
                )
            ]
        manifest = Path(backup_path) / "backup_manifest.json"
        return [self.check_file_exists(str(manifest), min_size=10)]
