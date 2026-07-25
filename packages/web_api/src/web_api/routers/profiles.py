from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from data_service.models import Profile
from data_service.schemas import ProfileCreate as ProfileCreateSchema
from data_service.schemas import ProfileUpdate as ProfileUpdateSchema
from data_service.service import DataService

from ..dependencies import get_active_profile, get_data_service
from ..schemas.responses import ExportResponse, ProfileResponse

router = APIRouter(
    prefix="/api/v1/fertility/profiles",
    tags=["profiles"],
)


@router.get("/", response_model=list[ProfileResponse])
async def list_profiles(
    data_svc: DataService = Depends(get_data_service),
) -> list[ProfileResponse]:
    profiles = await data_svc.profiles.get_all()
    return profiles  # type: ignore[return-value]


@router.post("/", response_model=ProfileResponse, status_code=201)
async def create_profile(
    body: ProfileCreateSchema,
    data_svc: DataService = Depends(get_data_service),
) -> ProfileResponse:
    existing = await data_svc.profiles.get_all()
    for p in existing:
        if p.name.lower() == body.name.lower():
            raise HTTPException(
                status_code=400,
                detail=f'A profile named "{body.name}" already exists.',
            )
    profile = await data_svc.create_profile(body.name, body.temp_unit)
    await data_svc.session.commit()
    return profile  # type: ignore[return-value]


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: UUID,
    data_svc: DataService = Depends(get_data_service),
) -> ProfileResponse:
    profile = await data_svc.profiles.get_by_id(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile  # type: ignore[return-value]


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: UUID,
    body: ProfileUpdateSchema,
    data_svc: DataService = Depends(get_data_service),
) -> ProfileResponse:
    profile = await data_svc.profiles.update_settings(
        profile_id,
        name=body.name,
        temp_unit=body.temp_unit,
        interpretation_method=body.interpretation_method,
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    await data_svc.session.commit()
    return profile  # type: ignore[return-value]


@router.post("/{profile_id}/activate", response_model=ProfileResponse)
async def activate_profile(
    profile_id: UUID,
    data_svc: DataService = Depends(get_data_service),
) -> ProfileResponse:
    profile = await data_svc.profiles.set_active(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    await data_svc.session.commit()
    return profile  # type: ignore[return-value]


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: UUID,
    data_svc: DataService = Depends(get_data_service),
    profile: Profile = Depends(get_active_profile),
) -> dict[str, str]:
    profiles = await data_svc.profiles.get_all()
    if len(profiles) <= 1:
        raise HTTPException(
            status_code=400, detail="Cannot delete the only profile."
        )
    if profile.id == profile_id:
        raise HTTPException(
            status_code=400, detail="Cannot delete the active profile."
        )
    success = await data_svc.profiles.delete(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    await data_svc.session.commit()
    return {"status": "deleted"}


@router.get("/{profile_id}/export", response_model=ExportResponse)
async def export_profile(
    profile_id: UUID,
    data_svc: DataService = Depends(get_data_service),
) -> ExportResponse:
    from datetime import datetime

    export_data = await data_svc.export_profile_data(profile_id)
    if export_data is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return ExportResponse(
        format="byrd-health-export",
        version=1,
        exported_at=datetime.now().isoformat(timespec="seconds"),
        profile=export_data["profile"],
        cycles=export_data["cycles"],
    )
