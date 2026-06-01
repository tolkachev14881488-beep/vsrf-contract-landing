"""Tests for delivery fallback chain."""

from __future__ import annotations

import pytest

from delivery import DeliveryError, deliver_application


@pytest.fixture
def sample_record():
    return {
        "name": "Иванов Иван Иванович",
        "phone": "+7 (999) 123-45-67",
        "age": 25,
        "region": "moscow",
        "comment": "",
        "consent": True,
        "created_at": "2026-06-01T12:00:00+00:00",
    }


def test_deliver_uses_web3forms_first(sample_record, monkeypatch):
    monkeypatch.setattr("delivery.web3forms_configured", lambda: True)
    monkeypatch.setattr("delivery.send_via_web3forms", lambda _r: None)
    assert deliver_application(sample_record) == "web3forms"


def test_deliver_raises_when_all_fail(sample_record, monkeypatch):
    monkeypatch.setattr("delivery.web3forms_configured", lambda: False)
    monkeypatch.setattr("delivery.email_configured", lambda: False)
    monkeypatch.setattr(
        "delivery.send_via_formsubmit",
        lambda _r: (_ for _ in ()).throw(__import__("formsubmit_notify").FormSubmitError("down")),
    )
    with pytest.raises(DeliveryError):
        deliver_application(sample_record)
