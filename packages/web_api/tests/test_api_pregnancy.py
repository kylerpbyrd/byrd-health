from datetime import date, timedelta


class TestPregnancyEndpoints:
    async def test_create_pregnancy_with_due_date_and_week(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "PregUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        lmp = date.today() - timedelta(days=14)
        response = await client.post(
            "/api/v1/fertility/pregnancy/",
            json={"cycle_id": cycle_id, "lmp_date": str(lmp)},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["cycle_id"] == cycle_id
        assert data["lmp_date"] == str(lmp)
        assert data["due_date"] is not None
        assert data["current_week"] is not None
        assert data["current_week"] >= 1
        assert data["trimester"] is not None
        assert data["trimester"] >= 1
        assert data["is_active"] is True
        assert data["id"] is not None

        expected_due = lmp + timedelta(days=280)
        assert data["due_date"] == str(expected_due)

    async def test_get_active_pregnancy(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "GetPregUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        lmp = date.today() - timedelta(days=10)
        create_preg = await client.post(
            "/api/v1/fertility/pregnancy/",
            json={"cycle_id": cycle_id, "lmp_date": str(lmp)},
        )
        assert create_preg.status_code == 201

        response = await client.get("/api/v1/fertility/pregnancy/")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        assert data["lmp_date"] == str(lmp)
        assert data["current_week"] is not None
        assert data["days_remaining"] is not None

    async def test_get_returns_404_when_no_pregnancy(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "NoPregUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.get("/api/v1/fertility/pregnancy/")
        assert response.status_code == 404

    async def test_post_rejects_duplicate_cycle(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "DupPregUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        lmp = date.today() - timedelta(days=7)
        first = await client.post(
            "/api/v1/fertility/pregnancy/",
            json={"cycle_id": cycle_id, "lmp_date": str(lmp)},
        )
        assert first.status_code == 201

        second = await client.post(
            "/api/v1/fertility/pregnancy/",
            json={"cycle_id": cycle_id, "lmp_date": str(lmp)},
        )
        assert second.status_code == 409

    async def test_patch_updates_notes(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "NotesPregUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        lmp = date.today() - timedelta(days=21)
        await client.post(
            "/api/v1/fertility/pregnancy/",
            json={"cycle_id": cycle_id, "lmp_date": str(lmp)},
        )

        response = await client.patch(
            "/api/v1/fertility/pregnancy/",
            json={"notes": "First ultrasound scheduled"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "First ultrasound scheduled"

    async def test_patch_sets_is_active_false_to_end_tracking(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "EndPregUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        lmp = date.today() - timedelta(days=30)
        await client.post(
            "/api/v1/fertility/pregnancy/",
            json={"cycle_id": cycle_id, "lmp_date": str(lmp)},
        )

        response = await client.patch(
            "/api/v1/fertility/pregnancy/",
            json={"is_active": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

        get_resp = await client.get("/api/v1/fertility/pregnancy/")
        assert get_resp.status_code == 404

    async def test_days_remaining_decrements_as_due_date_approaches(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "DaysPregUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        lmp = date.today() - timedelta(days=260)

        await client.post(
            "/api/v1/fertility/pregnancy/",
            json={"cycle_id": cycle_id, "lmp_date": str(lmp)},
        )

        response = await client.get("/api/v1/fertility/pregnancy/")
        assert response.status_code == 200
        data = response.json()
        assert data["days_remaining"] > 0
        assert data["trimester"] == 3
        assert data["current_week"] >= 37

    async def test_create_pregnancy_with_ovulation_date(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "OvPregUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        cycles_resp = await client.get("/api/v1/fertility/cycles/")
        cycle_id = cycles_resp.json()["cycles"][0]["id"]

        ovulation = date.today() - timedelta(days=30)
        response = await client.post(
            "/api/v1/fertility/pregnancy/",
            json={
                "cycle_id": cycle_id,
                "lmp_date": str(date.today() - timedelta(days=14)),
                "ovulation_date": str(ovulation),
            },
        )
        assert response.status_code == 201
        data = response.json()
        expected_due = ovulation + timedelta(days=266)
        assert data["due_date"] == str(expected_due)
