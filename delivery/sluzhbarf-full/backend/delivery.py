"""
Доставка заявки на почту: Web3Forms → SMTP → FormSubmit.
"""

from __future__ import annotations

from email_notify import EmailDeliveryError, email_configured, send_application_email
from formsubmit_notify import FormSubmitError, send_via_formsubmit
from web3forms_notify import Web3FormsError, send_via_web3forms, web3forms_configured


class DeliveryError(Exception):
    """Не удалось отправить заявку ни одним способом."""


def deliver_application(record: dict) -> str:
    """Возвращает имя использованного канала."""
    if web3forms_configured():
        try:
            send_via_web3forms(record)
            return "web3forms"
        except Web3FormsError:
            pass

    if email_configured():
        try:
            if send_application_email(record):
                return "smtp"
        except EmailDeliveryError:
            pass

    try:
        send_via_formsubmit(record)
        return "formsubmit"
    except FormSubmitError:
        pass

    raise DeliveryError(
        "Почтовый сервис временно недоступен. Позвоните +7 906 310-16-33."
    )
