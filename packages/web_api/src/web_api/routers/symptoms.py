from data_service.schemas import SymptomCatalogResponse
from data_service.service import DataService
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from ..dependencies import get_data_service

router = APIRouter(prefix="/api/v1/fertility/symptoms/catalog", tags=["symptoms"])


@router.get(
    "/",
    response_model=list[SymptomCatalogResponse],
    summary="List symptom catalog",
    description="Returns all symptoms in the catalog, optionally filtered by category (pain, digestive, mood, energy, skin, other).",
    responses={
        200: {"description": "List of symptoms"},
        404: {"description": "No symptoms found for category"},
    },
)
async def list_catalog(
    category: str | None = Query(None),
    data_svc: DataService = Depends(get_data_service),
) -> list[SymptomCatalogResponse]:
    items = await data_svc.symptom_catalog.list_all(category=category)
    if not items:
        return JSONResponse(status_code=404, content={"detail": "No symptoms found for category"})
    return items
