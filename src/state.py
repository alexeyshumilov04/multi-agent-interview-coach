"""
Session state and config: position, grade, experience, participant_name.
Types for LangGraph state (turns history, current question, internal_thoughts).
"""
from typing import TypedDict


class SessionConfig(TypedDict, total=False):
    """Input parameters for the interview session."""
    position: str
    grade: str
    experience: str
    participant_name: str


class TurnRecord(TypedDict):
    """One exchange: agent question + user answer + internal thoughts."""
    turn_id: int
    agent_visible_message: str
    user_message: str
    internal_thoughts: str


class SessionState(TypedDict, total=False):
    """State passed through LangGraph nodes."""
    config: SessionConfig
    current_question: str
    internal_thoughts: str
    observer_instruction: str
    turn_id: int
    history: list[TurnRecord]
    should_end: bool
    final_feedback: str
    user_message: str
