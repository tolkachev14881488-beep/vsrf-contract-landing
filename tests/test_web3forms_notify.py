"""Tests for Web3Forms delivery."""

from __future__ import annotations

import json

import pytest

import web3forms_notify
from web3forms_notify import Web3FormsError, build_web3forms_body, send_via_web3forms


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


def test_build_web3forms_body(sample_record):
    body = build_web3forms_body(sample_record, "test-key")
    assert body["access_key"] == "test-key"
    assert body["Регион"] == "Москва и МО"


def test_send_via_web3forms_success(sample_record, monkeypatch):
    monkeypatch.setattr(web3forms_notify, "WEB3FORMS_ACCESS_KEY", "secret")

    class FakeResponse:
        def read(self):
            return json.dumps({"success": True}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(web3forms_notify.urllib.request, "urlopen", lambda *a, **k: FakeResponse())
    send_via_web3forms(sample_record)


def test_send_without_key_raises(sample_record, monkeypatch):
    monkeypatch.setattr(web3forms_notify, "WEB3FORMS_ACCESS_KEY", "")
    with pytest.raises(Web3FormsError):
        send_via_web3forms(sample_record)
