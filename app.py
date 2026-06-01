"""
Backend for contract military service landing page.
Serves static files and handles application form submissions.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
APPLICATIONS_FILE = DATA_DIR / "applications.jsonl"

PHONE_PATTERN = re.compile(r"^\+7\s\(\d{3}\)\s\d{3}-\d{2}-\d{2}$")
NAME_PATTERN = re.compile(r"^[\w\s\-]+$", re.UNICODE)

VALID_REGIONS = {
    "moscow",
    "spb",
    "central",
    "south",
    "north",
    "volga",
    "ural",
    "siberia",
    "far-east",
    "other",
}

app = Flask(__name__, static_folder="static", static_url_path="/static")


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def validate_application(payload: dict) -> tuple[dict | None, str | None]:
    """Validate incoming JSON. Returns (clean_data, error_message)."""
    if not isinstance(payload, dict):
        return None, "Некорректный формат данных"

    name = (payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    region = (payload.get("region") or "").strip()
    comment = (payload.get("comment") or "").strip()
    consent = payload.get("consent")
    age = payload.get("age")

    if len(name) < 5:
        return None, "Укажите полное ФИО"
    if not NAME_PATTERN.match(name):
        return None, "ФИО содержит недопустимые символы"
    if len(name.split()) < 2:
        return None, "Укажите фамилию и имя"

    if not PHONE_PATTERN.match(phone):
        return None, "Некорректный формат телефона"

    try:
        age_int = int(age)
    except (TypeError, ValueError):
        return None, "Укажите корректный возраст"

    if age_int < 18 or age_int > 65:
        return None, "Возраст должен быть от 18 до 65 лет"

    if region not in VALID_REGIONS:
        return None, "Выберите регион из списка"

    if consent is not True:
        return None, "Требуется согласие на обработку данных"

    return {
        "name": name,
        "phone": phone,
        "age": age_int,
        "region": region,
        "comment": comment[:2000],
        "consent": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }, None


def save_application(record: dict) -> None:
    ensure_data_dir()
    with APPLICATIONS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/apply", methods=["POST"])
def apply():
    payload = request.get_json(silent=True)
    data, error = validate_application(payload or {})

    if error:
        return jsonify({"success": False, "error": error}), 400

    save_application(data)
    return jsonify({
        "success": True,
        "message": "Заявка принята",
        "id": data["created_at"],
    }), 201


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "vsrf-contract-landing"})


if __name__ == "__main__":
    ensure_data_dir()
    app.run(host="0.0.0.0", port=5000, debug=True)
