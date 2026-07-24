from datetime import date


class TestInsightsEndpoints:
    async def test_get_insights(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "InsightsUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get("/api/v1/fertility/insights/")
        assert response.status_code == 200
        data = response.json()
        assert "cycle_day" in data
        assert "phase" in data
        assert "coverline" in data
        assert "ovulation_date" in data
        assert "warnings" in data
        assert "next_period_date" in data

    async def test_get_insights_no_profile(self, client):
        response = await client.get("/api/v1/fertility/insights/")
        assert response.status_code == 404

    async def test_reanalyze_insights(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "ReanalyzeUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post("/api/v1/fertility/insights/reanalyze")
        assert response.status_code == 200
        data = response.json()
        assert "cycle_day" in data
        assert "phase" in data

    async def test_reanalyze_with_temp_data(self, client):
        import datetime as dt

        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Re1", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        for i in range(14):
            d = date.today() - dt.timedelta(days=13 - i)
            await client.post(
                "/api/v1/fertility/entries/",
                json={"date": str(d), "temp_value": 97.2 + (0.3 if i >= 7 else 0.0)},
            )

        response = await client.post("/api/v1/fertility/insights/reanalyze")
        assert response.status_code == 200
        data = response.json()
        assert "cycle_day" in data
        assert isinstance(data["cycle_day"], int)

    async def test_insights_has_warnings(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "WarnUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get("/api/v1/fertility/insights/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["warnings"], list)

    async def test_insights_with_entries(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "EntryInsights", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 97.5,
                "cervical_mucus": "watery",
                "symptoms": [{"symptom_type": "cramps", "severity": 1}],
            },
        )

        response = await client.get("/api/v1/fertility/insights/")
        assert response.status_code == 200
        data = response.json()
        assert data["cycle_day"] >= 1
        assert data["phase"] in {
            "menstruation",
            "pre_ovulatory",
            "fertile",
            "ovulation",
            "luteal",
        }
