"""
LangGraph workflow: reflection node (Observer + Interviewer) -> state with internal_thoughts and next question.
Main loop runs outside (get user input, invoke graph, log turn, show next question).
"""
from typing import Any

from langgraph.graph import END, START, StateGraph

from src.agents.interviewer import run_next_question
from src.agents.observer import run_observer
from src.state import SessionConfig, SessionState, TurnRecord


def _history_as_dicts(history: list[TurnRecord] | list[dict]) -> list[dict]:
    return [dict(h) for h in history]


def reflection_node(state: SessionState) -> dict[str, Any]:
    """
    Run Observer on last answer, then Interviewer with Observer's instruction.
    Return state updates: observer_instruction, internal_thoughts, current_question.
    """
    config = state.get("config") or {}
    history = _history_as_dicts(state.get("history") or [])
    current_question = state.get("current_question") or ""
    user_message = state.get("user_message") or ""

    position = config.get("position", "")
    grade = config.get("grade", "")
    experience = config.get("experience", "")

    observer_thought = run_observer(
        position=position,
        grade=grade,
        experience=experience,
        history=history,
        last_question=current_question,
        user_message=user_message,
    )

    next_question = run_next_question(
        position=position,
        grade=grade,
        experience=experience,
        history=history,
        observer_instruction=observer_thought,
    )

    # internal_thoughts format: [Observer]: ...\n[Interviewer]: ...\n
    internal_thoughts = f"[Observer]: {observer_thought.strip()}\n[Interviewer]: Сформировал следующий вопрос с учётом инструкции Observer.\n"

    return {
        "observer_instruction": observer_thought,
        "internal_thoughts": internal_thoughts,
        "current_question": next_question.strip(),
    }


def build_graph() -> StateGraph:
    """Build reflection graph: START -> reflection -> END."""
    graph = StateGraph(SessionState)
    graph.add_node("reflection", reflection_node)
    graph.add_edge(START, "reflection")
    graph.add_edge("reflection", END)
    return graph


def compile_graph():
    return build_graph().compile()
