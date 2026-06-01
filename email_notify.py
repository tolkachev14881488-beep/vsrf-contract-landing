"""
Отправка заявок на почту через SMTP (Mail.ru / bk.ru).
"""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage

NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "rodionova61@bk.ru").strip()
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.mail.ru").strip()
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", NOTIFY_EMAIL).strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "").strip()
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USER or NOTIFY_EMAIL).strip()
SMTP_USE_SSL = os.environ.get("SMTP_USE_SSL", "true").lower() in ("1", "true", "yes")

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


class EmailDeliveryError(Exception):
    """Не удалось отправить письмо с заявкой."""


def email_configured() -> bool:
    return bool(NOTIFY_EMAIL and SMTP_USER and SMTP_PASSWORD)


def build_application_email(record: dict) -> EmailMessage:
    region_label = REGION_LABELS.get(record["region"], record["region"])
    comment = record.get("comment") or "—"
    created = record.get("created_at", "")

    body = "\n".join(
        [
            "Новая заявка с лендинга «Служба по контракту в ВС РФ»",
            "",
            f"ФИО: {record['name']}",
            f"Телефон: {record['phone']}",
            f"Возраст: {record['age']}",
            f"Регион: {region_label}",
            f"Комментарий: {comment}",
            "",
            f"Время (UTC): {created}",
        ]
    )

    msg = EmailMessage()
    msg["Subject"] = f"Заявка: {record['name']} — {record['phone']}"
    msg["From"] = SMTP_FROM
    msg["To"] = NOTIFY_EMAIL
    msg.set_content(body)
    return msg


def send_application_email(record: dict) -> bool:
    """
    Отправляет заявку на NOTIFY_EMAIL.
    Возвращает True при успехе, False если SMTP не настроен.
  """
    if not email_configured():
        return False

    msg = build_application_email(record)

    try:
        if SMTP_USE_SSL:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=30) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.starttls(context=ssl.create_default_context())
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
    except OSError as exc:
        raise EmailDeliveryError("Ошибка соединения с почтовым сервером") from exc
    except smtplib.SMTPException as exc:
        raise EmailDeliveryError("Почтовый сервер отклонил отправку") from exc

    return True
