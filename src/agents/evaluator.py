"""
Evaluator agent: produces final verdict and structured feedback (Grade, Hiring, Confidence, Technical Review, Soft Skills, Roadmap).
Only this agent makes hire decision; Interviewer and Observer do not.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.messages import HumanMessage, SystemMessage

from config.llm import get_llm
from config.prompts import EVALUATOR_PROMPT, EVALUATOR_SYSTEM


def _format_full_history(turns: list[dict]) -> str:
    lines = []
    for t in turns:
        lines.append(f"Вопрос: {t.get('agent_visible_message', '')}")
        lines.append(f"Ответ кандидата: {t.get('user_message', '')}")
        lines.append(f"Внутренние мысли: {t.get('internal_thoughts', '')}")
        lines.append("---")
    return "\n".join(lines) if lines else "(нет данных)"


def run_evaluator(
    position: str,
    grade: str,
    experience: str,
    participant_name: str,
    turns: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
) -> str:
    llm = get_llm(model=model, temperature=temperature)
    human = EVALUATOR_PROMPT.format(
        position=position,
        grade=grade,
        experience=experience,
        participant_name=participant_name,
        full_history=_format_full_history(turns),
    )
    messages = [
        SystemMessage(content=EVALUATOR_SYSTEM),
        HumanMessage(content=human),
    ]
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)
