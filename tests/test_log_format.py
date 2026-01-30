"""Verify interview_log_*.json structure: participant_name, turns with turn_id/agent_visible_message/user_message/internal_thoughts, final_feedback."""
import json
import tempfile
from pathlib import Path

import pytest

# Assume src is on path when running from project root
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.logger import InterviewLogger, create_session, get_log_path


def test_log_path_auto_increment(tmp_path: Path) -> None:
    assert get_log_path(tmp_path, None).name == "interview_log_1.json"
    (tmp_path / "interview_log_1.json").write_text("{}")
    assert get_log_path(tmp_path, None).name == "interview_log_2.json"


def test_log_path_explicit_session(tmp_path: Path) -> None:
    assert get_log_path(tmp_path, 5).name == "interview_log_5.json"


def test_logger_structure(tmp_path: Path) -> None:
    logger = create_session(
        participant_name="Иван Иванов",
        log_dir=tmp_path,
        session_number=1,
    )
    logger.log_turn(
        turn_id=1,
        agent_visible_message="Расскажите про опыт в Python.",
        user_message="Я джун, пишу код 3 месяца.",
        internal_thoughts="[Observer]: Кандидат новичок.\n[Interviewer]: Нужно спросить про базовые типы данных.\n",
    )
    logger.log_final_feedback("Grade: Junior. Hiring: No Hire. Confidence: 70%.")

    path = tmp_path / "interview_log_1.json"
    assert path.exists()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    assert "participant_name" in data
    assert data["participant_name"] == "Иван Иванов"
    assert "turns" in data
    assert len(data["turns"]) == 1
    turn = data["turns"][0]
    assert turn["turn_id"] == 1
    assert "agent_visible_message" in turn
    assert "user_message" in turn
    assert "internal_thoughts" in turn
    assert "[Observer]" in turn["internal_thoughts"]
    assert "[Interviewer]" in turn["internal_thoughts"]
    assert "final_feedback" in data
    assert data["final_feedback"] != ""


def test_logger_multiple_turns(tmp_path: Path) -> None:
    logger = create_session("Test User", log_dir=tmp_path, session_number=2)
    for i in range(1, 4):
        logger.log_turn(
            turn_id=i,
            agent_visible_message=f"Question {i}",
            user_message=f"Answer {i}",
            internal_thoughts=f"[Observer]: ok\n[Interviewer]: next\n",
        )
    logger.log_final_feedback("Done.")

    with open(tmp_path / "interview_log_2.json", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["turns"]) == 3
    assert data["turns"][2]["turn_id"] == 3
    assert data["final_feedback"] == "Done."
