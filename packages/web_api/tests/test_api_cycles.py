from datetime import date


class TestCycleEndpoints:
    async def test_list_cycles_empty(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CycleUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get("/api/v1/fertility/cycles/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["cycles"]) >= 1
        assert data["cycles"][0]["is_active"] is True

    async def test_get_current_cycle(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CurrentCycle", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get("/api/v1/fertility/cycles/current")
        assert response.status_code == 200
        data = response.json()
        assert data["start_date"] == str(date.today())
        assert data["end_date"] is None
        assert "temperatures" in data
        assert "signs" in data
        assert "symptoms" in data

    async def test_get_current_cycle_no_profile(self, client):
        response = await client.get("/api/v1/fertility/cycles/current")
        assert response.status_code == 404

    async def test_get_cycle_by_id(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "CycleDetail", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        response = await client.get(f"/api/v1/fertility/cycles/{cycle_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == cycle_id
        assert "temperatures" in data
        assert "signs" in data
        assert "symptoms" in data
        assert data["profile_id"] == profile_id

    async def test_get_cycle_not_found(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "NotFoundCycle", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get(
            "/api/v1/fertility/cycles/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404

    async def test_get_cycle_chart(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "ChartUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        await client.post(
            "/api/v1/fertility/entries/",
            json={
                "date": str(date.today()),
                "temp_value": 97.5,
                "cervical_mucus": "watery",
                "opk_result": "negative",
            },
        )

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        response = await client.get(f"/api/v1/fertility/cycles/{cycle_id}/chart")
        assert response.status_code == 200
        data = response.json()
        assert "labels" in data
        assert "temperatures" in data
        assert "discarded" in data
        assert "coverline" in data
        assert "mucus" in data
        assert "opk" in data
        assert data["unit"] == "F"

    async def test_get_cycle_chart_not_found(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Chart404", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get(
            "/api/v1/fertility/cycles/00000000-0000-0000-0000-000000000000/chart"
        )
        assert response.status_code == 404

    async def test_cycle_with_entry_data(self, client):
        import datetime as dt

        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "DataCycle", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycle_start = date.today()
        for i in range(3):
            d = cycle_start + dt.timedelta(days=i)
            await client.post(
                "/api/v1/fertility/entries/",
                json={
                    "date": str(d),
                    "temp_value": 97.0 + i * 0.5,
                    "menstrual_flow": "medium" if i == 0 else "",
                },
            )

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        response = await client.get(f"/api/v1/fertility/cycles/{cycle_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["temperatures"]) == 3
        assert len(data["signs"]) == 1

    async def test_start_new_cycle(self, client):
        from datetime import timedelta

        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "NewCycle", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        future_date = date.today() + timedelta(days=7)

        response = await client.post(
            "/api/v1/fertility/cycles/",
            json={"start_date": str(future_date)},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["start_date"] == str(future_date)

    async def test_start_new_cycle_before_current(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "BeforeCycle", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/cycles/",
            json={"start_date": str(date.today())},
        )
        assert response.status_code == 400
        assert "after" in response.json()["detail"]
