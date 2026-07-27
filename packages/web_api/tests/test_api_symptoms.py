import pytest_asyncio
from data_service.models import SymptomCatalog


SEED_SYMPTOMS = [
    {"name": "Cramps", "category": "pain", "severity_scale": 3},
    {"name": "Headache", "category": "pain", "severity_scale": 3},
    {"name": "Back Pain", "category": "pain", "severity_scale": 3},
    {"name": "Breast Tenderness", "category": "pain", "severity_scale": 3},
    {"name": "Ovulation Pain", "category": "pain", "severity_scale": 3},
    {"name": "Bloating", "category": "digestive", "severity_scale": 3},
    {"name": "Nausea", "category": "digestive", "severity_scale": 3},
    {"name": "Constipation", "category": "digestive", "severity_scale": 3},
    {"name": "Diarrhea", "category": "digestive", "severity_scale": 3},
    {"name": "Food Cravings", "category": "digestive", "severity_scale": 3},
    {"name": "Irritability", "category": "mood", "severity_scale": 3},
    {"name": "Anxiety", "category": "mood", "severity_scale": 3},
    {"name": "Depression", "category": "mood", "severity_scale": 3},
    {"name": "Mood Swings", "category": "mood", "severity_scale": 3},
    {"name": "Fatigue", "category": "energy", "severity_scale": 3},
    {"name": "Insomnia", "category": "energy", "severity_scale": 3},
    {"name": "High Energy", "category": "energy", "severity_scale": 3},
    {"name": "Low Energy", "category": "energy", "severity_scale": 3},
    {"name": "Acne", "category": "skin", "severity_scale": 3},
    {"name": "Dry Skin", "category": "skin", "severity_scale": 3},
    {"name": "Oily Skin", "category": "skin", "severity_scale": 3},
    {"name": "Spotting", "category": "other", "severity_scale": 3},
    {"name": "Hot Flashes", "category": "other", "severity_scale": 3},
    {"name": "Dizziness", "category": "other", "severity_scale": 3},
]


@pytest_asyncio.fixture
async def seeded_catalog(async_session):
    for s in SEED_SYMPTOMS:
        async_session.add(SymptomCatalog(**s))
    await async_session.commit()


class TestSymptomCatalog:
    async def test_get_catalog_returns_all_24_symptoms(self, client, seeded_catalog):
        response = await client.get("/api/v1/fertility/symptoms/catalog/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 24
        categories = {item["category"] for item in data}
        assert categories == {"pain", "digestive", "mood", "energy", "skin", "other"}

    async def test_get_catalog_filtered_by_category(self, client, seeded_catalog):
        response = await client.get(
            "/api/v1/fertility/symptoms/catalog/?category=pain"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        for item in data:
            assert item["category"] == "pain"

    async def test_get_catalog_returns_404_for_unknown_category(self, client, seeded_catalog):
        response = await client.get(
            "/api/v1/fertility/symptoms/catalog/?category=nonexistent"
        )
        assert response.status_code == 404
        assert "No symptoms found" in response.json()["detail"]
