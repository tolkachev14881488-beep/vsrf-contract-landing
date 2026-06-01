# Служба по контракту — лендинг ВС РФ

Современный одностраничный сайт для рекламного привлечения кандидатов на службу по контракту в Вооружённых Силах Российской Федерации.

## Стек

- **HTML5** — семантическая разметка, доступность
- **CSS3** — глубокая камуфляжная палитра (хаки), анимации, адаптив
- **JavaScript** — навигация, валидация, маска телефона, отправка формы
- **Python (Flask)** — API приёма заявок, сохранение в JSONL, отправка на почту

## Структура

```
vsrf/
├── index.html
├── app.py
├── requirements.txt
├── static/
│   ├── css/style.css
│   └── js/main.js
├── data/                  # создаётся при первой заявке
│   └── applications.jsonl
└── tests/
    ├── test_app.py
    └── TEST_CASES.md
```

## Онлайн

**Сайт (GitHub Pages):** https://tolkachev14881488-beep.github.io/vsrf-contract-landing/

Для работы формы заявок разверните бэкенд на [Render](https://render.com/deploy?repo=https://github.com/tolkachev14881488-beep/vsrf-contract-landing) (бесплатный план). После деплоя API будет доступен по адресу `https://vsrf-contract-landing.onrender.com`.

### Почта для заявок

Заявки отправляются на **rodionova61@bk.ru** (SMTP Mail.ru).

1. Войдите в почту [mail.ru](https://mail.ru) / bk.ru → **Настройки** → **Пароль и безопасность** → **Пароли для внешних приложений** — создайте пароль.
2. На Render в сервисе **Environment** добавьте переменную `SMTP_PASSWORD` (значение — созданный пароль). Остальные переменные уже заданы в `render.yaml`.
3. Локально скопируйте `.env.example` в `.env` и укажите `SMTP_PASSWORD`.

Проверка: `GET /api/health` → `"email_configured": true`.

## Локальный запуск

```bash
pip install -r requirements.txt
python app.py
```

Сайт: http://127.0.0.1:5000

## Тесты

```bash
pytest tests/ -v
```

Подробные ручные тест-кейсы: [tests/TEST_CASES.md](tests/TEST_CASES.md)

## API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/health` | Проверка работоспособности |
| POST | `/api/apply` | Приём заявки (JSON) |

Пример тела запроса:

```json
{
  "name": "Иванов Иван Иванович",
  "phone": "+7 (999) 123-45-67",
  "age": 25,
  "region": "moscow",
  "comment": "Мотострелки",
  "consent": true
}
```

## Примечание

Сайт носит информационный характер. Для официальной рекламы используйте согласованные формулировки и контакты пунктов отбора Минобороны РФ.
