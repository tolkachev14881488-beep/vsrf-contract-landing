"""
Отправка заявок через Web3Forms (работает, когда FormSubmit недоступен).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

WEB3FORMS_ACCESS_KEY = os.environ.get("WEB3FORMS_ACCESS_KEY", "").strip()
WEB3FORMS_URL = "https://api.web3forms.com/submit"
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "rodionova61@bk.ru").strip()

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


class Web3FormsError(Exception):
    """Не удалось отправить заявку через Web3Forms."""


def web3forms_configured() -> bool:
    return bool(WEB3FORMS_ACCESS_KEY)


def build_web3forms_body(record: dict, access_key: str | None = None) -> dict:
    region_label = REGION_LABELS.get(record["region"], record["region"])
    comment = record.get("comment") or "—"
    return {
        "access_key": access_key or WEB3FORMS_ACCESS_KEY,
        "subject": f"Заявка: {record['name']} — {record['phone']}",
        "from_name": "Лендинг — служба по контракту ВС РФ",
        "replyto": NOTIFY_EMAIL,
        "ФИО": record["name"],
        "Телефон": record["phone"],
        "Возраст": str(record["age"]),
        "Регион": region_label,
        "Комментарий": comment,
    }


def send_via_web3forms(record: dict, access_key: str | None = None) -> None:
    key = (access_key or WEB3FORMS_ACCESS_KEY).strip()
    if not key:
        raise Web3FormsError("Не настроен ключ Web3Forms")

    payload = json.dumps(build_web3forms_body(record, key)).encode("utf-8")
    req = urllib.request.Request(
        WEB3FORMS_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise Web3FormsError(
            "Сервис отправки недоступен. Позвоните +7 906 310-16-33."
        ) from exc

    if not body.get("success"):
        message = body.get("message") or "Web3Forms не принял заявку"
        raise Web3FormsError(message)
