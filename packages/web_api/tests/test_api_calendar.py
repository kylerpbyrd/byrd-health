from datetime import date


class TestCalendarEndpoint:
    async def test_calendar_no_profile(self, client):
        response = await client.get("/api/v1/fertility/calendar/?month=2026-07")
        assert response.status_code == 404

    async def test_calendar_returns_42_days(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CalUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get("/api/v1/fertility/calendar/?month=2026-07")
        assert response.status_code == 200
        data = response.json()

        assert data["month"] == "2026-07"
        assert data["profile"]["slug"]
        assert data["profile"]["temp_unit"] == "F"

        assert len(data["days"]) == 42

        days = data["days"]
        first = days[0]["date"]
        last = days[41]["date"]
        assert first < last
        assert first <= "2026-07-01" <= last

        not_current = [d for d in days if not d["in_current_month"]]
        current = [d for d in days if d["in_current_month"]]
        assert len(not_current) > 0
        assert len(current) > 0
        assert len(current) >= 28

    async def test_calendar_with_entries(self, client):

        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CalEntry", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        today = date.today()
        this_month = f"{today.year}-{today.month:02d}"

        await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(today),
                "temp_value": 97.5,
                "cervical_mucus": "watery",
                "opk_result": "positive",
            },
        )

        response = await client.get(
            f"/api/v1/fertility/calendar/?month={this_month}"
        )
        assert response.status_code == 200
        data = response.json()
        days = data["days"]

        today_entry = None
        for d in days:
            if d["date"] == str(today):
                today_entry = d
                break

        assert today_entry is not None
        assert today_entry["is_today"] is True
        assert today_entry["has_entry"] is True
        assert today_entry["in_current_month"] is True

    async def test_calendar_has_cycles_in_range(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CalCycles", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        today = date.today()
        this_month = f"{today.year}-{today.month:02d}"

        await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(today),
                "temp_value": 97.5,
            },
        )

        response = await client.get(
            f"/api/v1/fertility/calendar/?month={this_month}"
        )
        assert response.status_code == 200
        data = response.json()

        assert "cycles_in_range" in data
        cycles = data["cycles_in_range"]
        assert len(cycles) >= 1

        cycle = cycles[0]
        assert "id" in cycle
        assert "start_date" in cycle
        assert "phase_dates" in cycle

    async def test_calendar_invalid_month(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CalBad", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get("/api/v1/fertility/calendar/?month=not-valid")
        assert response.status_code == 422

    async def test_calendar_day_flags(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CalFlags", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        today = date.today()
        this_month = f"{today.year}-{today.month:02d}"

        await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(today),
                "temp_value": 97.5,
            },
        )

        response = await client.get(
            f"/api/v1/fertility/calendar/?month={this_month}"
        )
        assert response.status_code == 200
        data = response.json()

        for day in data["days"]:
            assert isinstance(day["is_period_start"], bool)
            assert isinstance(day["is_ovulation_day"], bool)
            assert isinstance(day["is_fertile"], bool)
            assert isinstance(day["is_today"], bool)
            assert isinstance(day["has_entry"], bool)
            assert isinstance(day["in_current_month"], bool)
            assert "date" in day
            assert isinstance(day["cycle_day"], int) or day["cycle_day"] is None
