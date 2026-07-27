class TestMedicationEndpoints:
    async def test_post_creates_medication(self, client, test_app):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "MedUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/medications/",
            json={
                "name": "Ibuprofen",
                "dosage": "200mg",
                "schedule": "as_needed",
                "notes": "For headache",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Ibuprofen"
        assert data["dosage"] == "200mg"
        assert data["schedule"] == "as_needed"
        assert data["notes"] == "For headache"
        assert data["id"] is not None
        assert data["taken_at"] is not None

    async def test_get_lists_medications(self, client, test_app):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "MedListUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        await client.post(
            "/api/v1/fertility/medications/",
            json={"name": "Tylenol", "dosage": "500mg"},
        )
        await client.post(
            "/api/v1/fertility/medications/",
            json={"name": "Prenatal Vitamin", "schedule": "daily"},
        )

        response = await client.get("/api/v1/fertility/medications/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = {m["name"] for m in data}
        assert names == {"Tylenol", "Prenatal Vitamin"}

    async def test_post_validates_required_fields(self, client, test_app):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "ValidUser", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]
        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.post(
            "/api/v1/fertility/medications/",
            json={"schedule": "daily"},
        )
        assert response.status_code == 422
