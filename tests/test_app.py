"""
Test cases for contract service landing — API and validation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import VALID_REGIONS, app, validate_application


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def valid_payload():
    return {
        "name": "Иванов Иван Иванович",
        "phone": "+7 (999) 123-45-67",
        "age": 25,
        "region": "moscow",
        "comment": "Хочу служить в мотострелках",
        "consent": True,
    }


class TestHealthEndpoint:
  """TC-001: Health check availability."""

  def test_health_returns_ok(self, client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "vsrf-contract-landing"
    assert "email_configured" in data


class TestIndexPage:
  """TC-002: Main landing page is served."""

  def test_index_returns_html(self, client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data.lower()
    assert "Служба по контракту".encode() in response.data


class TestApplicationValidation:
  """TC-003–TC-010: Server-side form validation."""

  def test_valid_payload_passes(self, valid_payload):
    data, error = validate_application(valid_payload)
    assert error is None
    assert data["name"] == valid_payload["name"]
    assert data["region"] == "moscow"
    assert data["consent"] is True

  def test_short_name_rejected(self, valid_payload):
    valid_payload["name"] = "Ив"
    _, error = validate_application(valid_payload)
    assert error is not None

  def test_single_word_name_rejected(self, valid_payload):
    valid_payload["name"] = "Иванов"
    _, error = validate_application(valid_payload)
    assert error is not None

  def test_invalid_phone_rejected(self, valid_payload):
    valid_payload["phone"] = "89991234567"
    _, error = validate_application(valid_payload)
    assert error is not None

  def test_age_below_18_rejected(self, valid_payload):
    valid_payload["age"] = 17
    _, error = validate_application(valid_payload)
    assert error is not None

  def test_age_above_63_rejected(self, valid_payload):
    valid_payload["age"] = 64
    _, error = validate_application(valid_payload)
    assert error is not None

  def test_invalid_region_rejected(self, valid_payload):
    valid_payload["region"] = "invalid-region"
    _, error = validate_application(valid_payload)
    assert error is not None

  def test_consent_required(self, valid_payload):
    valid_payload["consent"] = False
    _, error = validate_application(valid_payload)
    assert error is not None

  def test_all_regions_are_valid_keys(self):
    for region in VALID_REGIONS:
      payload = {
        "name": "Петров Пётр Петрович",
        "phone": "+7 (900) 111-22-33",
        "age": 30,
        "region": region,
        "consent": True,
      }
      data, error = validate_application(payload)
      assert error is None, f"Region {region} should be valid"
      assert data["region"] == region


class TestApplyEndpoint:
  """TC-011–TC-014: Application submission API."""

  def test_successful_submission(self, client, valid_payload, tmp_path, monkeypatch):
    test_file = tmp_path / "applications.jsonl"
    monkeypatch.setattr("app.APPLICATIONS_FILE", test_file)
    monkeypatch.setattr("app.DATA_DIR", tmp_path)
    response = client.post(
      "/api/apply",
      data=json.dumps(valid_payload),
      content_type="application/json",
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert "id" in body

    assert test_file.exists()
    lines = test_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    saved = json.loads(lines[0])
    assert saved["name"] == valid_payload["name"]

  def test_invalid_submission_returns_400(self, client, valid_payload):
    valid_payload["age"] = 10
    response = client.post(
      "/api/apply",
      data=json.dumps(valid_payload),
      content_type="application/json",
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert "error" in body

  def test_empty_body_returns_400(self, client):
    response = client.post(
      "/api/apply",
      data=json.dumps({}),
      content_type="application/json",
    )
    assert response.status_code == 400

  def test_comment_truncation(self, valid_payload):
    valid_payload["comment"] = "а" * 3000
    data, error = validate_application(valid_payload)
    assert error is None
    assert len(data["comment"]) == 2000


class TestSeoMeta:
  """TC-014: SEO tags and structured data on landing page."""

  def test_seo_meta_and_json_ld(self, client):
    response = client.get("/")
    html = response.data.decode("utf-8")
    assert response.status_code == 200
    assert 'name="description"' in html
    assert "canonical" in html
    assert 'property="og:title"' in html
    assert "application/ld+json" in html
    assert "FAQPage" in html


class TestStaticAssets:
  """TC-015–TC-016: Static resources availability."""

  def test_css_available(self, client):
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert b"khaki" in response.data.lower() or b"--khaki" in response.data

  def test_js_available(self, client):
    response = client.get("/static/js/main.js")
    assert response.status_code == 200
    assert b"validateForm" in response.data or b"/api/apply" in response.data

  def test_robots_txt(self, client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"Sitemap:" in response.data

  def test_sitemap_xml(self, client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert b"<urlset" in response.data
