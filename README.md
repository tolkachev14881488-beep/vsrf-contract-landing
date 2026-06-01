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

### Почта для заявок (Web3Forms)

FormSubmit иногда недоступен; используется [Web3Forms](https://web3forms.com) → письма на **rodionova61@bk.ru**.

1. Откройте https://web3forms.com  
2. Укажите **rodionova61@bk.ru** → **Create Access Key**  
3. Скопируйте ключ и добавьте в `index.html`:  
   `<meta name="web3forms-access-key" content="ВАШ_КЛЮЧ">`  
   **или** в Render → Environment → `WEB3FORMS_ACCESS_KEY` (для отправки через API).

После этого форма на GitHub Pages отправляет заявки без FormSubmit.

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
