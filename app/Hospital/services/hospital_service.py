

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from Hospital.repositories.HospitalRepository import (
    get_hospital_name,
    hospital_name_exists,
    updateHospitalname,
    createHospital,
)
from Hospital.schemas.Hospital import (
    HospitalCreate,
    HospitalCreateResponse,
    HospitalNameUpdate,
    HospitalNameUpdateResponse,
)


def create_hospital(
    request: HospitalCreate,
    db: Session,
) -> HospitalCreateResponse:
    if hospital_name_exists(request.hospitalName, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A hospital with this name already exists",
        )

    hospital = createHospital(request.hospitalName, request.City, db)
    db.commit()
    return HospitalCreateResponse(
        hospitalID=hospital.hospitalID,
        hospitalName=hospital.hospitalName,
        City=hospital.City,
    )


def rename_hospital(
    request: HospitalNameUpdate,
    db: Session,
) -> HospitalNameUpdateResponse:
    old_name = get_hospital_name(request.hospitalID, db)
    if old_name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found",
        )

    if old_name.strip().casefold() == request.hospitalName.casefold():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The new hospital name is the same as the current name",
        )

    if hospital_name_exists(request.hospitalName, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Another hospital already uses this name",
        )

    updated = updateHospitalname(
        request.hospitalName,
        db,
        request.hospitalID,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found",
        )

    db.commit()
    return HospitalNameUpdateResponse(
        oldName=old_name,
        newName=request.hospitalName,
    )
