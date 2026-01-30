"""
Interview session logger. Writes interview_log_{scenario_number}.json
with participant_name, turns (turn_id, agent_visible_message, user_message, internal_thoughts), final_feedback.
"""
import json
import re
from pathlib import Path
from typing import Any


def _next_session_number(log_dir: Path) -> int:
    """Find next scenario number from existing interview_log_*.json in log_dir."""
    if not log_dir.exists():
        return 1
    pattern = re.compile(r"interview_log_(\d+)\.json")
    numbers = []
    for f in log_dir.iterdir():
        if f.is_file():
            m = pattern.match(f.name)
            if m:
                numbers.append(int(m.group(1)))
    return max(numbers, default=0) + 1


def get_log_path(log_dir: Path, session_number: int | None = None) -> Path:
    """Resolve log file path. If session_number is None, auto-increment from existing files."""
    log_dir = Path(log_dir)
    if session_number is not None:
        return log_dir / f"interview_log_{session_number}.json"
    n = _next_session_number(log_dir)
    return log_dir / f"interview_log_{n}.json"


def create_session(
    participant_name: str,
    log_dir: Path | str = ".",
    session_number: int | None = None,
) -> "InterviewLogger":
    """Create a new session and return a logger that writes to interview_log_{N}.json."""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    path = get_log_path(log_dir, session_number)
    return InterviewLogger(participant_name=participant_name, log_path=path)


class InterviewLogger:
    """Appends turns and final_feedback to interview_log_{N}.json."""

    def __init__(self, participant_name: str, log_path: Path | str):
        self.participant_name = participant_name
        self.log_path = Path(log_path)
        self._data: dict[str, Any] = {
            "participant_name": participant_name,
            "turns": [],
            "final_feedback": "",
        }

    def log_turn(
        self,
        turn_id: int,
        agent_visible_message: str,
        user_message: str,
        internal_thoughts: str,
    ) -> None:
        """Append one turn to in-memory state and persist to JSON."""
        self._data["turns"].append(
            {
                "turn_id": turn_id,
                "agent_visible_message": agent_visible_message,
                "user_message": user_message,
                "internal_thoughts": internal_thoughts,
            }
        )
        self._save()

    def log_final_feedback(self, final_feedback: str) -> None:
        """Set final_feedback and persist to JSON."""
        self._data["final_feedback"] = final_feedback
        self._save()

    def _save(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    @property
    def turns(self) -> list[dict[str, Any]]:
        return self._data["turns"]
