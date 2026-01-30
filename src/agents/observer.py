"""
Observer agent: analyzes candidate answers, checks facts, gives instructions to Interviewer.
Output is internal thought only (for internal_thoughts log).
"""
import sys
from pathlib import Path

# Allow importing config from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.messages import HumanMessage, SystemMessage

from config.llm import get_llm
from config.prompts import OBSERVER_REFLECTION, OBSERVER_SYSTEM


def _format_history(history: list[dict]) -> str:
    lines = []
    for t in history:
        lines.append(f"В: {t.get('agent_visible_message', '')}")
        lines.append(f"О: {t.get('user_message', '')}")
    return "\n".join(lines) if lines else "(нет предыдущих реплик)"


def create_observer_chain(model: str | None = None, temperature: float = 0.3):
    llm = get_llm(model=model, temperature=temperature)

    def reflect(
        position: str,
        grade: str,
        experience: str,
        history: list[dict],
        last_question: str,
        user_message: str,
    ) -> str:
        human = OBSERVER_REFLECTION.format(
            position=position,
            grade=grade,
            experience=experience,
            history=_format_history(history),
            last_question=last_question,
            user_message=user_message,
        )
        messages = [
            SystemMessage(content=OBSERVER_SYSTEM),
            HumanMessage(content=human),
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)

    return reflect


def run_observer(
    position: str,
    grade: str,
    experience: str,
    history: list[dict],
    last_question: str,
    user_message: str,
    model: str | None = None,
) -> str:
    chain = create_observer_chain(model=model)
    return chain(
        position=position,
        grade=grade,
        experience=experience,
        history=history,
        last_question=last_question,
        user_message=user_message,
    )
