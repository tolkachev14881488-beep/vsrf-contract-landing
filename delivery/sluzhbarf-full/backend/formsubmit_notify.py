"""
Отправка заявок на почту через FormSubmit (серверный прокси, без CORS).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from urllib.parse import quote

NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "rodionova61@bk.ru").strip()
FORMSUBMIT_URL = f"https://formsubmit.co/ajax/{quote(NOTIFY_EMAIL)}"

REGION_LABELS = {
    "moscow": "Москва и МО",
    "spb": "Санкт-Петербург и ЛО",
    "central": "Центральный ФО",
    "south": "Южный ФО",
    "north": "Северо-Западный ФО",
    "volga": "Приволжский ФО",
    "ural": "Уральский ФО",
    "siberia": "Сибирский ФО",
    "far-east": "Дальневосточный ФО",
    "other": "Другой",
}


class FormSubmitError(Exception):
    """Не удалось отправить заявку через FormSubmit."""


def build_formsubmit_body(record: dict) -> dict:
    region_label = REGION_LABELS.get(record["region"], record["region"])
    return {
        "_subject": f"Заявка: {record['name']} — {record['phone']}",
        "_template": "table",
        "_captcha": "false",
        "ФИО": record["name"],
        "Телефон": record["phone"],
        "Возраст": str(record["age"]),
        "Регион": region_label,
        "Комментарий": record.get("comment") or "—",
    }


def send_via_formsubmit(record: dict) -> None:
    payload = json.dumps(build_formsubmit_body(record)).encode("utf-8")
    req = urllib.request.Request(
        FORMSUBMIT_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "vsrf-contract-landing/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw).get("message", raw)
        except json.JSONDecodeError:
            detail = raw or "Ошибка сервиса FormSubmit"
        raise FormSubmitError(detail) from exc
    except urllib.error.URLError as exc:
        raise FormSubmitError(
            "Сервис отправки временно недоступен. Позвоните +7 906 310-16-33."
        ) from exc

    if body.get("success") not in (True, "true"):
        message = body.get("message") or "FormSubmit не принял заявку"
        raise FormSubmitError(message)
