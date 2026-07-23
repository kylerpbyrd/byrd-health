import importlib.util
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Load the application with an isolated SQLite database for each test."""
    monkeypatch.setenv("DATA_PATH", str(tmp_path))
    monkeypatch.setenv("BBT_TEMP_UNIT", "F")
    sys.path.insert(0, str(APP_DIR))

    for module_name in ("bbt_tracker_app", "db", "ha_client"):
        sys.modules.pop(module_name, None)

    spec = importlib.util.spec_from_file_location(
        "bbt_tracker_app", APP_DIR / "app.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.init_db()
    module.app.config.update(TESTING=True)
    module.app.bbt_module = module
    monkeypatch.setattr(module, "_trigger_analysis", lambda *_args: None)

    with module.app.test_client() as test_client:
        yield test_client

    sys.path.remove(str(APP_DIR))


def test_dashboard_creates_a_default_profile_and_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"BBT Fertility Tracker" in response.data


def test_api_entry_requires_a_temperature_value(client):
    response = client.post("/api/entry", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "temp_value required"


def test_api_entry_rejects_a_non_numeric_temperature(client):
    response = client.get("/")
    assert response.status_code == 200

    response = client.post("/api/entry", json={"temp_value": "not-a-temperature"})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Temperature must be a numeric value"


def test_api_entry_rejects_an_implausible_temperature(client):
    client.get("/")

    response = client.post("/api/entry", json={"temp_value": 70})

    assert response.status_code == 400
    assert "Temperature must be between" in response.get_json()["error"]


def test_chart_data_cannot_be_read_from_another_profile(client):
    client.get("/")
    module = client.application.bbt_module
    db = module.get_db()
    try:
        profile_id = db.execute(
            "INSERT INTO profiles (name, slug, temp_unit) VALUES ('Other', 'other', 'F')"
        ).lastrowid
        cycle_id = db.execute(
            "INSERT INTO cycles (profile_id, start_date) VALUES (?, '2026-01-01')",
            (profile_id,),
        ).lastrowid
        db.commit()
    finally:
        db.close()

    response = client.get(f"/api/chart-data/{cycle_id}")

    assert response.status_code == 404


def test_profile_export_is_a_json_download(client):
    client.get("/")

    response = client.get("/export")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert "attachment;" in response.headers["Content-Disposition"]
    assert response.get_json()["format"] == "bbt-fertility-tracker-export"


def test_database_records_the_baseline_schema_migration(client):
    client.get("/")
    module = client.application.bbt_module
    db = module.get_db()
    try:
        versions = [row["version"] for row in db.execute("SELECT version FROM schema_migrations")]
    finally:
        db.close()

    assert versions == [1]
