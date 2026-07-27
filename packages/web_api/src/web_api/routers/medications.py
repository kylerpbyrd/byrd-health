from data_service.models import Profile
from data_service.schemas import MedicationCreate, MedicationResponse
from data_service.service import DataService
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import get_active_profile, get_data_service

router = APIRouter(prefix="/api/v1/fertility/medications", tags=["medications"])


@router.get(
    "/",
    response_model=list[MedicationResponse],
    summary="List medications",
    description="Returns all medications for the active profile, ordered by most recently taken.",
    responses={
        200: {"description": "List of medications"},
    },
)
async def list_medications(
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> list[MedicationResponse]:
    return await data_svc.medications.list_all(profile.id)


@router.post(
    "/",
    status_code=201,
    response_model=MedicationResponse,
    summary="Log medication",
    description="Records a medication taken by the active profile.",
    responses={
        201: {"description": "Medication logged"},
        400: {"description": "Invalid medication data"},
    },
)
async def log_medication(
    body: MedicationCreate,
    profile: Profile = Depends(get_active_profile),
    data_svc: DataService = Depends(get_data_service),
) -> MedicationResponse:
    if not body.name.strip():
        return JSONResponse(status_code=400, content={"detail": "Medication name is required"})

    return await data_svc.medications.create(
        profile_id=profile.id,
        name=body.name.strip(),
        dosage=body.dosage.strip() if body.dosage else None,
        schedule=body.schedule,
        notes=body.notes.strip() if body.notes else None,
    )
