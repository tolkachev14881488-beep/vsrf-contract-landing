"""Tests for FormSubmit proxy."""

from __future__ import annotations

import json
from io import BytesIO

import pytest

import formsubmit_notify
from formsubmit_notify import FormSubmitError, build_formsubmit_body, send_via_formsubmit


@pytest.fixture
def sample_record():
    return {
        "name": "Иванов Иван Иванович",
        "phone": "+7 (999) 123-45-67",
        "age": 25,
        "region": "moscow",
        "comment": "Тест",
        "consent": True,
        "created_at": "2026-06-01T12:00:00+00:00",
    }


def test_build_formsubmit_body(sample_record):
    body = build_formsubmit_body(sample_record)
    assert body["ФИО"] == sample_record["name"]
    assert body["Регион"] == "Москва и МО"
    assert "Заявка:" in body["_subject"]


def test_send_via_formsubmit_success(sample_record, monkeypatch):
    class FakeResponse:
        def read(self):
            return json.dumps({"success": "true"}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(formsubmit_notify.urllib.request, "urlopen", lambda *a, **k: FakeResponse())
    send_via_formsubmit(sample_record)


def test_send_via_formsubmit_failure(sample_record, monkeypatch):
    class FakeResponse:
        def read(self):
            return json.dumps({"success": "false", "message": "Not activated"}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(formsubmit_notify.urllib.request, "urlopen", lambda *a, **k: FakeResponse())

    with pytest.raises(FormSubmitError, match="Not activated"):
        send_via_formsubmit(sample_record)
