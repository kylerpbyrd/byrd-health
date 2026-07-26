from datetime import date


class TestEntryEndpoints:
    async def test_create_entry(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "EntryUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 97.5,
                "time_taken": "06:30:00",
                "cervical_mucus": "watery",
                "notes": "Test entry",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["temperature"] is not None
        assert data["temperature"]["temp_value"] == 97.5
        assert data["signs"] is not None
        assert data["signs"]["cervical_mucus"] == "watery"

    async def test_create_entry_no_active_profile(self, client):
        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 97.5,
            },
        )
        assert response.status_code == 404

    async def test_create_entry_temp_out_of_range_f(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "TempUserF", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 110.0,
            },
        )
        assert response.status_code == 422
        assert "Temperature must be between" in response.json()["detail"]

    async def test_create_entry_temp_out_of_range_c(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "TempUserC", "temp_unit": "C"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 25.0,
            },
        )
        assert response.status_code == 422
        assert "Temperature must be between" in response.json()["detail"]

    async def test_create_entry_with_symptoms(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "SymptomUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 97.8,
                "symptoms": [
                    {"symptom_type": "cramps", "severity": 2},
                    {"symptom_type": "headache", "severity": 1},
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["symptoms"]) == 2

    async def test_create_entry_with_all_signs(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "SignsUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 97.9,
                "menstrual_flow": "light",
                "cervical_mucus": "creamy",
                "cervical_position": "medium",
                "cervical_firmness": "soft",
                "cervical_opening": "open",
                "opk_result": "negative",
                "notes": "Full entry",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["signs"]["menstrual_flow"] == "light"
        assert data["signs"]["cervical_mucus"] == "creamy"
        assert data["signs"]["cervical_position"] == "medium"
        assert data["signs"]["opk_result"] == "negative"

    async def test_create_entry_discarded_temp(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "DiscardUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 99.0,
                "is_discarded": True,
                "discard_reason": "Slept poorly",
            },
        )
        assert response.status_code == 201
        assert response.json()["temperature"]["is_discarded"] is True
        assert response.json()["temperature"]["discard_reason"] == "Slept poorly"

    async def test_create_entry_period_start(self, client):
        from datetime import timedelta

        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "PeriodUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        future_date = date.today() + timedelta(days=7)

        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(future_date),
                "temp_value": 97.4,
                "is_period_start": True,
                "menstrual_flow": "medium",
            },
        )
        assert response.status_code == 201

    async def test_get_today_entry_empty(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "TodayUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get("/api/v1/fertility/entries/today")
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] is None
        assert data["signs"] is None
        assert data["symptoms"] == []

    async def test_get_today_entry_with_data(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "TodayData", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 97.9,
                "cervical_mucus": "egg_white",
            },
        )

        response = await client.get("/api/v1/fertility/entries/today")
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] is not None
        assert data["temperature"]["temp_value"] == 97.9
        assert data["signs"]["cervical_mucus"] == "egg_white"

    async def test_create_entry_celsius_profile(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CelsiusUser", "temp_unit": "C"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 36.5,
            },
        )
        assert response.status_code == 201
        assert response.json()["temperature"]["temp_value"] == 36.5
