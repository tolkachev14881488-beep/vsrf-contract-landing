"""Tests for application email notifications."""

from __future__ import annotations

import pytest

import email_notify
from email_notify import EmailDeliveryError, build_application_email, send_application_email


@pytest.fixture
def sample_record():
    return {
        "name": "Иванов Иван Иванович",
        "phone": "+7 (999) 123-45-67",
        "age": 25,
        "region": "moscow",
        "comment": "БПЛА",
        "consent": True,
        "created_at": "2026-06-01T12:00:00+00:00",
    }


def test_build_application_email(sample_record, monkeypatch):
    monkeypatch.setattr(email_notify, "NOTIFY_EMAIL", "rodionova61@bk.ru")
    monkeypatch.setattr(email_notify, "SMTP_FROM", "rodionova61@bk.ru")
    msg = build_application_email(sample_record)
    assert msg["To"] == "rodionova61@bk.ru"
    body = msg.get_content()
    assert "Иванов Иван Иванович" in body
    assert "Москва и МО" in body
    assert "БПЛА" in body


def test_send_skipped_without_password(sample_record, monkeypatch):
    monkeypatch.setattr(email_notify, "SMTP_PASSWORD", "")
    assert send_application_email(sample_record) is False


def test_send_raises_on_smtp_error(sample_record, monkeypatch):
    monkeypatch.setattr(email_notify, "SMTP_PASSWORD", "secret")
    monkeypatch.setattr(email_notify, "SMTP_USER", "rodionova61@bk.ru")
    monkeypatch.setattr(email_notify, "NOTIFY_EMAIL", "rodionova61@bk.ru")

    class FailingSMTP:
        def __init__(self, *args, **kwargs):
            raise OSError("connection refused")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(email_notify.smtplib, "SMTP_SSL", FailingSMTP)

    with pytest.raises(EmailDeliveryError):
        send_application_email(sample_record)
