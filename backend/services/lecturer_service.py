import io
from typing import List

import openpyxl
from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Lecturer
from backend.schemas.lecturer import LecturerCreate, LecturerResponse, LecturerUpdate


async def create_lecturer(session: AsyncSession, data: LecturerCreate) -> LecturerResponse:
    new_lecturer = Lecturer(
        lecturer_id=data.lecturer_id,
        name=data.name,
        program_id=data.program_id,
    )
    session.add(new_lecturer)
    await session.commit()
    await session.refresh(new_lecturer)
    return LecturerResponse.model_validate(new_lecturer)


async def get_all_lecturers(session: AsyncSession) -> List[LecturerResponse]:
    result = await session.execute(select(Lecturer))
    lecturers = result.scalars().all()
    return [LecturerResponse.model_validate(lecturer) for lecturer in lecturers]


async def find_lecturer_by_id(session: AsyncSession, lecturer_id: str) -> LecturerResponse:
    lecturer = await session.get(Lecturer, lecturer_id)
    if not lecturer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lecturer not found: {lecturer_id}")
    return LecturerResponse.model_validate(lecturer)


async def delete_lecturer(session: AsyncSession, lecturer_id: str) -> None:
    lecturer = await session.get(Lecturer, lecturer_id)
    if not lecturer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lecturer not found: {lecturer_id}")
    await session.delete(lecturer)
    await session.commit()


async def update_lecturer(session: AsyncSession, lecturer_id: str, lecturer_update: LecturerUpdate) -> LecturerResponse:
    lecturer = await session.get(Lecturer, lecturer_id)
    if not lecturer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lecturer not found: {lecturer_id}")

    update_data = lecturer_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(lecturer, field, value)

    await session.commit()
    await session.refresh(lecturer)
    return LecturerResponse.model_validate(lecturer)


async def _process_excel(session: AsyncSession, file_contents: bytes):
    workbook = openpyxl.load_workbook(io.BytesIO(file_contents))
    sheet = workbook.active

    successful = []
    failed = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or not row[0] or not row[1]:
            continue
        lecturer_id = str(row[0]).strip()
        name = str(row[1]).strip()
        program_id = str(row[2]).strip() if len(row) > 2 and row[2] else lecturer_id

        # Check duplicates
        existing = await session.execute(
            select(Lecturer).where(or_(Lecturer.lecturer_id == lecturer_id, Lecturer.name == name))
        )
        if existing.scalar():
            failed.append({"lecturer_id": lecturer_id, "name": name, "error": "User already exists"})
            continue

        new_lecturer = Lecturer(
            lecturer_id=lecturer_id,
            name=name,
            program_id=program_id,
        )
        session.add(new_lecturer)
        successful.append({"lecture_id": lecturer_id, "name": name, "program_id": program_id})

    await session.commit()
    return {"successful": successful, "failed": failed}


async def create_multiple_lecturers_from_excel(session: AsyncSession, file_contents: bytes):
    return await _process_excel(session, file_contents)