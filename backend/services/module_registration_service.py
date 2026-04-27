import io
from typing import List

import openpyxl
from fastapi import HTTPException, status
from sqlalchemy import select, func, case, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import ModuleRegistration, Attendance
from backend.models.enums import AttendanceStatus
from backend.schemas.module_registration import ModuleRegistrationCreate, ModuleRegistrationResponse, \
    ModuleRegistrationUpdate


async def create_registration(session: AsyncSession, data: ModuleRegistrationCreate) -> ModuleRegistrationResponse:
    registration = ModuleRegistration(
        student_id=data.student_id,
        module_id=data.module_id,
        lecturer_id=data.lecturer_id,
    )
    session.add(registration)
    await session.commit()
    await session.refresh(registration)
    return ModuleRegistrationResponse.model_validate(registration)


async def get_all_registrations(session: AsyncSession) -> List[ModuleRegistrationResponse]:
    result = await session.execute(select(ModuleRegistration))
    rows = result.scalars().all()
    return [ModuleRegistrationResponse.model_validate(row) for row in rows]


async def find_registration_by_id(session: AsyncSession, module_reg_id: int) -> ModuleRegistrationResponse:
    row = await session.get(ModuleRegistration, module_reg_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return ModuleRegistrationResponse.model_validate(row)


async def find_registrations_by_student_id(session: AsyncSession, student_id: str) -> List[ModuleRegistrationResponse]:
    result = await session.execute(select(ModuleRegistration).where(ModuleRegistration.student_id == student_id))
    rows = result.scalars().all()
    return [ModuleRegistrationResponse.model_validate(row) for row in rows]


async def find_registrations_by_module_id(session: AsyncSession, module_id: str) -> List[ModuleRegistrationResponse]:
    result = await session.execute(select(ModuleRegistration).where(ModuleRegistration.module_id == module_id))
    rows = result.scalars().all()
    return [ModuleRegistrationResponse.model_validate(row) for row in rows]


async def get_lecturer_modules_with_student_count(session: AsyncSession, lecturer_id: str) -> list[dict]:
    result = await session.execute(
        select(ModuleRegistration.module_id, func.count(ModuleRegistration.student_id))
        .where(ModuleRegistration.lecturer_id == lecturer_id)
        .group_by(ModuleRegistration.module_id)
    )
    rows = result.all()
    return [{"module_id": module_id, "student_count": count} for module_id, count in rows]


async def get_all_modules_with_student_count_and_attendance_rate(session: AsyncSession) -> list[dict]:
    reg_result = await session.execute(
        select(ModuleRegistration.module_id, func.count(ModuleRegistration.student_id))
        .group_by(ModuleRegistration.module_id)
    )
    registrations = reg_result.all()
    att_result = await session.execute(
        select(
            Attendance.module_id,
            func.count(Attendance.attendance_id).label("total"),
            func.sum(case((Attendance.attendance_status == AttendanceStatus.PRESENT, 1), else_=0)).label("PRESENT"),
        ).group_by(Attendance.module_id)
    )
    attendance = att_result.all()
    att_map = {module_id: (total or 0, present or 0) for module_id, total, present in attendance}
    payload = []
    for module_id, student_count in registrations:
        total, present = att_map.get(module_id, (0, 0))
        rate = (present / total * 100.0) if total else 0.0
        payload.append({"module_id": module_id, "student_count": student_count, "attendance_rate": round(rate, 2)})
    return payload


async def update_registration(session: AsyncSession, module_reg_id: int, data: ModuleRegistrationUpdate) -> ModuleRegistrationResponse:
    row = await session.get(ModuleRegistration, module_reg_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    await session.commit()
    await session.refresh(row)
    return ModuleRegistrationResponse.model_validate(row)


async def delete_registration(session: AsyncSession, module_reg_id: int) -> None:
    row = await session.get(ModuleRegistration, module_reg_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    await session.delete(row)
    await session.commit()


async def _process_excel(session: AsyncSession, file_contents: bytes):
    workbook = openpyxl.load_workbook(io.BytesIO(file_contents))
    sheet = workbook.active

    successful = []
    failed = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or not row[0] or not row[1]:
            continue

        student_id = str(row[0]).strip()
        module_id = str(row[1]).strip()
        lecturer_id = str(row[2]).strip() if len(row) > 2 and row[2] else ""


        # Check duplicates
        existing = await session.execute(
            select(ModuleRegistration).where(or_(ModuleRegistration.module_id == module_id, ModuleRegistration.student_id == student_id))
        )
        if existing.scalar():
            failed.append({"module_id": module_id, "student_id": student_id, "error": "User already exists"})
            continue

        new_user = ModuleRegistration(
            student_id=student_id,
            module_id=module_id,
            lecturer_id=lecturer_id,
        )
        session.add(new_user)
        successful.append({ "student_id": student_id, "module_id": module_id, "lecturer_id": lecturer_id})

    await session.commit()
    return {"successful": successful, "failed": failed}


async def create_multiple_module_registration_from_excel(session: AsyncSession, file_contents: bytes):
    return await _process_excel(session, file_contents)