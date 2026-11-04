# 🤖 Multi-Agent Interview Coach

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-1C3C3C?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![OpenAI Compatible](https://img.shields.io/badge/LLM-OpenAI%20Compatible-412991?style=flat-square&logo=openai&logoColor=white)
![pytest](https://img.shields.io/badge/Tested%20with-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![AITUNNEL](https://img.shields.io/badge/LLM%20Provider-AITUNNEL-blueviolet?style=flat-square)

Система из нескольких AI-агентов для проведения технического интервью: **Interviewer** ведёт диалог, **Observer** анализирует ответы «в кулуарах» и даёт инструкции, **Evaluator** формирует финальный фидбек. Реализованы скрытая рефлексия, контекст, адаптивность сложности и устойчивость к оффтопу/галлюцинациям.

## 📋 Требования

- 🐍 Python 3.10+
- 🔑 Доступ к LLM через платформу **AITUNNEL** (OpenAI-совместимый API)

## ⚙️ Установка

```bash
cd multi-agent-interview-coach
pip install -r requirements.txt
cp .env.example .env
# Отредактируйте .env и укажите AITUNNEL_API_KEY (ключ из AITUNNEL)
```

## 🚀 Запуск

Из корня проекта:

```bash
python -m src.main --position "Python Developer" --grade "Middle" --experience "2 года" --participant-name "Иван Иванов"
```

Или с явным номером сценария и папкой для логов:

```bash
python -m src.main -p "Backend Developer" -g "Junior" -e "6 месяцев" -n "Петр Петров" --session 1 --log-dir ./logs --max-turns 15
```

Параметры:

| Параметр | Короткий | Описание |
|----------|----------|----------|
| `--position` | `-p` | Позиция (например: Python Developer) |
| `--grade` | `-g` | Грейд: Junior / Middle / Senior |
| `--experience` | `-e` | Опыт кандидата (например: 1 год) |
| `--participant-name` | `-n` | Имя участника (попадает в лог как `participant_name`) |
| `--session` | `-s` | Номер сценария (файл `interview_log_{N}.json`). Не указан — автоинкремент |
| `--log-dir` | `-d` | Папка для логов (по умолчанию: текущая) |
| `--max-turns` | `-m` | Максимум вопросов (по умолчанию: 15) |

Завершение интервью: система сгенерирует финальный фидбек и сохранит лог.

## 📝 Формат лога

Файл: `interview_log_{номер_сценария}.json` (в `--log-dir`).

Структура:

```json
{
  "participant_name": "Иван Иванов",
  "turns": [
    {
      "turn_id": 1,
      "agent_visible_message": "<вопрос агента>",
      "user_message": "<ответ пользователя>",
      "internal_thoughts": "[Observer]: <мысль>\n[Interviewer]: <мысль>\n"
    }
  ],
  "final_feedback": "<структурированный фидбек>"
}
```

`internal_thoughts` — внутренние «мысли» агентов (Observer и Interviewer), не показываемые кандидату.

## 🧾 Финальный фидбек

После команды завершения генерируется структурированный отчёт:

- **А. Вердикт:** Grade (Junior/Middle/Senior), Hiring Recommendation (Hire/No Hire/Strong Hire), Confidence Score (0–100%)
- **Б. Hard Skills:** Confirmed Skills, Knowledge Gaps (с правильными ответами по проваленным темам)
- **В. Soft Skills & Communication:** Clarity, Honesty, Engagement
- **Г. Roadmap:** темы и технологии для подтягивания (опционально — ссылки)

## 🔐 Переменные окружения

- `AITUNNEL_API_KEY` — ключ от платформы, которая предоставляет доступ к LLM (обязателен для работы по умолчанию)

Файл `.env` в корне проекта подхватывается автоматически (см. `.env.example`).

## 📂 Структура проекта

```
multi-agent-interview-coach/
├── .env.example
├── README.md
├── requirements.txt
├── config/
│   ├── prompts.py       # системные промпты агентов
│   └── llm.py           # клиент LLM (AITUNNEL: base_url, api_key)
├── src/
│   ├── main.py          # CLI, цикл интервью
│   ├── state.py         # типы состояния
│   ├── logger.py        # запись interview_log_{N}.json
│   ├── graph.py         # LangGraph: рефлексия (Observer + Interviewer)
│   ├── feedback.py      # генерация финального фидбека
│   └── agents/
│       ├── interviewer.py
│       ├── observer.py
│       └── evaluator.py
└── tests/
    └── test_log_format.py
```

## 🧪 Тесты

```bash
# из корня проекта
python -m pytest tests/test_log_format.py -v
```

Проверяется структура JSON-лога: наличие `participant_name`, `turns` с полями `turn_id`, `agent_visible_message`, `user_message`, `internal_thoughts`, и `final_feedback`.
