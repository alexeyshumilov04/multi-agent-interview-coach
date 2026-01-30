"""
Interviewer agent: conducts dialogue, asks questions. Uses Observer instruction to form next question.
Output is agent_visible_message shown to the candidate.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.messages import HumanMessage, SystemMessage

from config.llm import get_llm
from config.prompts import (
    INTERVIEWER_FIRST_QUESTION,
    INTERVIEWER_NEXT_QUESTION,
    INTERVIEWER_SYSTEM,
)


def _format_history(history: list[dict]) -> str:
    lines = []
    for t in history:
        lines.append(f"В: {t.get('agent_visible_message', '')}")
        lines.append(f"О: {t.get('user_message', '')}")
    return "\n".join(lines) if lines else "(нет предыдущих реплик)"


def create_interviewer_chain(model: str | None = None, temperature: float = 0.5):
    llm = get_llm(model=model, temperature=temperature)

    def first_question(position: str, grade: str, experience: str) -> str:
        human = INTERVIEWER_FIRST_QUESTION.format(
            position=position,
            grade=grade,
            experience=experience,
        )
        messages = [
            SystemMessage(content=INTERVIEWER_SYSTEM),
            HumanMessage(content=human),
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    def next_question(
        position: str,
        grade: str,
        experience: str,
        history: list[dict],
        observer_instruction: str,
    ) -> str:
        human = INTERVIEWER_NEXT_QUESTION.format(
            position=position,
            grade=grade,
            experience=experience,
            history=_format_history(history),
            observer_instruction=observer_instruction,
        )
        messages = [
            SystemMessage(content=INTERVIEWER_SYSTEM),
            HumanMessage(content=human),
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    return first_question, next_question


def run_first_question(
    position: str,
    grade: str,
    experience: str,
    model: str | None = None,
) -> str:
    first_fn, _ = create_interviewer_chain(model=model)
    return first_fn(position=position, grade=grade, experience=experience)


def run_next_question(
    position: str,
    grade: str,
    experience: str,
    history: list[dict],
    observer_instruction: str,
    model: str | None = None,
) -> str:
    _, next_fn = create_interviewer_chain(model=model)
    return next_fn(
        position=position,
        grade=grade,
        experience=experience,
        history=history,
        observer_instruction=observer_instruction,
    )
