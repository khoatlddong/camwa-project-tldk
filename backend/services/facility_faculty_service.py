from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import FacilityFaculty
from backend.schemas.facility_faculty import FacilityFacultyResponse, FacilityFacultyCreate, FacilityFacultyUpdate


async def create_facility_faculty(session: AsyncSession, data: FacilityFacultyCreate) -> FacilityFacultyResponse:
    new_facility_faculty = FacilityFaculty(
        staff_id=data.staff_id,
        name=data.name,
        program_id=data.program_id,
    )
    session.add(new_facility_faculty)
    await session.commit()
    await session.refresh(new_facility_faculty)
    return FacilityFacultyResponse.model_validate(new_facility_faculty)


async def get_all_facility_faculty(session: AsyncSession) -> list[FacilityFacultyResponse]:
    result = await session.execute(select(FacilityFaculty))
    facility_faculties = result.scalars().all()
    return [FacilityFacultyResponse.model_validate(facility_faculty) for facility_faculty in facility_faculties]


async def find_facility_faculty_by_id(session: AsyncSession, staff_id: str) -> FacilityFacultyResponse:
    facility_faculty = await session.get(FacilityFaculty, staff_id)
    if not facility_faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility Faculty not found")
    return FacilityFacultyResponse.model_validate(facility_faculty)


async def delete_facility_faculty(session: AsyncSession, staff_id: str) -> None:
    facility_faculty = await session.get(FacilityFaculty, staff_id)
    if not facility_faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility Faculty not found")
    await session.delete(facility_faculty)
    await session.commit()


async def update_facility_faculty(session: AsyncSession, staff_id: str, data: FacilityFacultyUpdate) -> FacilityFacultyResponse:
    faculty = await session.get(FacilityFaculty, staff_id)
    if not faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Facility Faculty not found")

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(faculty, field, value)

    await session.commit()
    await session.refresh(faculty)
    return FacilityFacultyResponse.model_validate(faculty)