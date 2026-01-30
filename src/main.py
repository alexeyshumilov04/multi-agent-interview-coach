"""
CLI: run interview session. Args: position, grade, experience, participant_name, session number.
Loop: show question -> get user answer -> reflection (Observer + Interviewer) -> log turn -> next question.
При намерении пользователя завершить интервью (фраза или подстрока в ответе) или при достижении max_turns:
сессия завершается, итоговый фидбек генерируется и записывается в JSON-лог вместе с turns.
"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on path for config and src
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv

load_dotenv(_project_root / ".env")

from src.graph import compile_graph
from src.logger import create_session
from src.agents.interviewer import run_first_question
from src.feedback import generate_final_feedback
from src.state import SessionConfig, SessionState, TurnRecord

# Точное совпадение ответа с одной из фраз — завершить интервью
STOP_PHRASES = frozenset(
    s.strip().lower()
    for s in (
        "стоп интервью",
        "закончить",
        "finish",
        "stop",
        "end",
        "завершить",
        "хватит",
        "закончим",
        "всё",
        "достаточно",
    )
)

# Подстроки в ответе, по которым считаем, что пользователь проявляет намерение завершить интервью
INTENT_END_SUBSTRINGS = (
    "стоп интервью",
    "закончить интервью",
    "закончим интервью",
    "завершить интервью",
    "на этом всё",
    "на этом закончим",
    "давайте закончим",
    "можно заканчивать",
    "хватит вопросов",
    "хочу закончить",
    "хочу завершить",
    "готов закончить",
    "достаточно вопросов",
    "всё, спасибо",
    "спасибо, достаточно",
    "finish",
    "stop interview",
    "end interview",
)

DEFAULT_MAX_TURNS = 15


def _user_wants_to_end(user_message: str) -> bool:
    """Проверяет, проявляет ли пользователь в ответе намерение завершить интервью."""
    if not user_message or not user_message.strip():
        return False
    msg = user_message.strip().lower()
    if msg in STOP_PHRASES:
        return True
    if any(msg.startswith(p) for p in STOP_PHRASES):
        return True
    # Проверка по подстрокам (намерение в свободной форме)
    return any(sub in msg for sub in INTENT_END_SUBSTRINGS)


def _finish_session(
    logger,
    position: str,
    grade: str,
    experience: str,
    participant_name: str,
) -> None:
    """
    Завершает сессию интервью: генерирует итоговый фидбек, записывает его в JSON-лог
    вместе с turns, выводит фидбек пользователю.
    """
    final_feedback = generate_final_feedback(
        position=position,
        grade=grade,
        experience=experience,
        participant_name=participant_name,
        turns=logger.turns,
    )
    logger.log_final_feedback(final_feedback)
    print("\n" + "=" * 60)
    print("Финальный фидбек:")
    print("=" * 60)
    print(final_feedback)
    print("\nЛог сохранён (включая итоговый фидбек):", logger.log_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multi-Agent Interview Coach: technical interview with Observer + Interviewer."
    )
    parser.add_argument("--position", "-p", required=True, help="Позиция (например: Python Developer)")
    parser.add_argument("--grade", "-g", required=True, help="Грейд (Junior / Middle / Senior)")
    parser.add_argument("--experience", "-e", required=True, help="Опыт кандидата (например: 1 год)")
    parser.add_argument("--participant-name", "-n", required=True, help="Имя участника (participant_name в логе)")
    parser.add_argument("--session", "-s", type=int, default=None, help="Номер сценария (interview_log_{N}.json)")
    parser.add_argument("--log-dir", "-d", default=".", help="Папка для interview_log_*.json")
    parser.add_argument("--max-turns", "-m", type=int, default=DEFAULT_MAX_TURNS, help="Максимум вопросов")
    args = parser.parse_args()

    config: SessionConfig = {
        "position": args.position,
        "grade": args.grade,
        "experience": args.experience,
        "participant_name": args.participant_name,
    }

    logger = create_session(
        participant_name=args.participant_name,
        log_dir=args.log_dir,
        session_number=args.session,
    )

    # Step 0: first question (not logged)
    current_question = run_first_question(
        position=args.position,
        grade=args.grade,
        experience=args.experience,
    )
    history: list[TurnRecord] = []
    graph = compile_graph()
    turn_id = 0

    while True:
        turn_id += 1
        if turn_id > args.max_turns:
            print("\nДостигнут лимит вопросов. Завершаем интервью.")
            _finish_session(
                logger=logger,
                position=args.position,
                grade=args.grade,
                experience=args.experience,
                participant_name=args.participant_name,
            )
            break

        print("\n" + "-" * 60)
        print(current_question)
        print("-" * 60)
        user_message = input(
            # (для завершения интервью напишите, например: «Стоп интервью», «Закончить», «Давайте закончим» и т.п.)
            "Ваш ответ: "
        ).strip()
        if not user_message:
            user_message = "(нет ответа)"

        # Reflection: Observer + Interviewer -> internal_thoughts + next_question
        initial_state: SessionState = {
            "config": config,
            "history": history,
            "current_question": current_question,
            "user_message": user_message,
            "turn_id": turn_id,
        }
        result = graph.invoke(initial_state)
        internal_thoughts = result.get("internal_thoughts") or ""
        next_question = result.get("current_question") or ""

        # Log this turn
        logger.log_turn(
            turn_id=turn_id,
            agent_visible_message=current_question,
            user_message=user_message,
            internal_thoughts=internal_thoughts,
        )
        history.append({
            "turn_id": turn_id,
            "agent_visible_message": current_question,
            "user_message": user_message,
            "internal_thoughts": internal_thoughts,
        })

        # Завершение интервью по намерению пользователя: генерируем фидбек и записываем в JSON
        if _user_wants_to_end(user_message):
            _finish_session(
                logger=logger,
                position=args.position,
                grade=args.grade,
                experience=args.experience,
                participant_name=args.participant_name,
            )
            break

        current_question = next_question


if __name__ == "__main__":
    main()
