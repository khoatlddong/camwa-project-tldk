from datetime import datetime, timezone, date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from backend.models import Semester
from backend.schemas.semester import SemesterCreate, SemesterResponse, SemesterUpdate


async def create_semester(session: AsyncSession, data: SemesterCreate) -> SemesterResponse:
    semester = Semester(
        sem_id=data.sem_id,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    session.add(semester)
    await session.commit()
    await session.refresh(semester)
    return SemesterResponse.model_validate(semester)


async def get_all_semester(session: AsyncSession) -> list[SemesterResponse]:
    result = await session.execute(select(Semester).order_by(Semester.start_date.desc()))
    semesters = result.scalars().all()
    return [SemesterResponse.model_validate(semester) for semester in semesters]


async def find_semester_by_id(session: AsyncSession, sem_id: str) -> SemesterResponse:
    semester = await session.get(Semester, sem_id)
    if not semester:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")
    return SemesterResponse.model_validate(semester)


async def update_semester(session: AsyncSession, sem_id: str, data: SemesterUpdate) -> SemesterResponse:
    semester = await session.get(Semester, sem_id)
    if not semester:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(semester, field, value)

    await session.commit()
    await session.refresh(semester)
    return SemesterResponse.model_validate(semester)


async def delete_semester(session: AsyncSession, sem_id: str) -> None:
    semester = await session.get(Semester, sem_id)
    if not semester:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Semester not found")
    await session.delete(semester)
    await session.commit()


async def get_current_semester(session: AsyncSession) -> SemesterResponse:
    now = datetime.now()
    result = await session.execute(
        select(Semester)
        .where(Semester.start_date <= now)
        .where(Semester.end_date >= now)
        .order_by(Semester.start_date.desc())
    )
    semester = result.scalars().first()
    if not semester:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No current semester found")
    return SemesterResponse.model_validate(semester)