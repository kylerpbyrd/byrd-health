import pytest


class TestProfileEndpoints:
    async def test_list_profiles_empty(self, client):
        response = await client.get("/api/v1/fertility/profiles/")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_profile(self, client):
        response = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Alice", "temp_unit": "F"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Alice"
        assert data["slug"] == "alice"
        assert data["temp_unit"] == "F"
        assert data["is_active"] is False
        assert "id" in data

    async def test_create_profile_duplicate_name(self, client):
        await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Bob", "temp_unit": "F"},
        )
        response = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Bob", "temp_unit": "C"},
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_create_profile_default_temp_unit(self, client):
        response = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Charlie"},
        )
        assert response.status_code == 201
        assert response.json()["temp_unit"] == "F"

    async def test_get_profile_by_id(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Dana", "temp_unit": "C"},
        )
        profile_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/fertility/profiles/{profile_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Dana"
        assert response.json()["temp_unit"] == "C"

    async def test_get_profile_not_found(self, client):
        response = await client.get(
            "/api/v1/fertility/profiles/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404

    async def test_update_profile(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Eve", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]

        response = await client.patch(
            f"/api/v1/fertility/profiles/{profile_id}",
            json={"temp_unit": "C", "interpretation_method": "conservative"},
        )
        assert response.status_code == 200
        assert response.json()["temp_unit"] == "C"
        assert response.json()["interpretation_method"] == "conservative"

    async def test_update_profile_not_found(self, client):
        response = await client.patch(
            "/api/v1/fertility/profiles/00000000-0000-0000-0000-000000000000",
            json={"temp_unit": "C"},
        )
        assert response.status_code == 404

    async def test_activate_profile(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "ActiveOne", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]

        response = await client.post(
            f"/api/v1/fertility/profiles/{profile_id}/activate"
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is True

    async def test_activate_profile_not_found(self, client):
        response = await client.post(
            "/api/v1/fertility/profiles/00000000-0000-0000-0000-000000000000/activate"
        )
        assert response.status_code == 404

    async def test_delete_profile(self, client):
        await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Keep", "temp_unit": "F"},
        )
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Remove", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]

        response = await client.delete(f"/api/v1/fertility/profiles/{profile_id}")
        assert response.status_code == 200
        assert response.json() == {"status": "deleted"}

    async def test_delete_last_profile(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Only", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]

        await client.post(f"/api/v1/fertility/profiles/{profile_id}/activate")

        response = await client.delete(f"/api/v1/fertility/profiles/{profile_id}")
        assert response.status_code == 400
        assert "Cannot delete" in response.json()["detail"]

    async def test_delete_active_profile(self, client):
        await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Active", "temp_unit": "F"},
        )
        create_resp2 = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "Other", "temp_unit": "F"},
        )

        await client.post(f"/api/v1/fertility/profiles/{create_resp2.json()['id']}/activate")

        response = await client.delete(
            f"/api/v1/fertility/profiles/{create_resp2.json()['id']}"
        )
        assert response.status_code == 400
        assert "active profile" in response.json()["detail"]

    async def test_export_profile(self, client):
        create_resp = await client.post(
            "/api/v1/fertility/profiles/",
            json={"name": "ExportMe", "temp_unit": "F"},
        )
        profile_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/fertility/profiles/{profile_id}/export")
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "byrd-health-export"
        assert data["version"] == 1
        assert data["profile"]["name"] == "ExportMe"

    async def test_export_profile_not_found(self, client):
        response = await client.get(
            "/api/v1/fertility/profiles/00000000-0000-0000-0000-000000000000/export"
        )
        assert response.status_code == 404
