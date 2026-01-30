"""
Final feedback: call Evaluator agent with full history (turns + internal_thoughts)
and return structured final_feedback string for interview_log.
"""
from typing import Any

from src.agents.evaluator import run_evaluator


def generate_final_feedback(
    position: str,
    grade: str,
    experience: str,
    participant_name: str,
    turns: list[dict[str, Any]],
    model: str | None = None,
) -> str:
    """
    Generate structured final feedback (Verdict, Hard Skills, Soft Skills, Roadmap).
    turns: list of {turn_id, agent_visible_message, user_message, internal_thoughts}.
    """
    return run_evaluator(
        position=position,
        grade=grade,
        experience=experience,
        participant_name=participant_name,
        turns=turns,
        model=model,
    )
