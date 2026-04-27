import io
from typing import List

import openpyxl
from fastapi import HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Student, ModuleRegistration, Attendance, Exam
from backend.schemas.student import StudentCreate, StudentResponse, StudentUpdate


async def create_student(session: AsyncSession, data: StudentCreate) -> StudentResponse:
    student = Student(
        student_id=data.student_id,
        name=data.name,
        map_location=data.map_location,
        program_id=data.program_id,
        intake=data.intake,
    )
    session.add(student)
    await session.commit()
    await session.refresh(student)
    return StudentResponse.model_validate(student)


async def get_all_students(session: AsyncSession) -> List[StudentResponse]:
    result = await session.execute(select(Student))
    students = result.scalars().all()
    return [StudentResponse.model_validate(student) for student in students]


async def find_student_by_id(session: AsyncSession, student_id: str) -> StudentResponse:
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return StudentResponse.model_validate(student)


async def delete_student(session: AsyncSession, student_id: str) -> None:
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    await session.delete(student)
    await session.commit()


async def update_student(session: AsyncSession, student_id: str, data: StudentUpdate) -> StudentResponse:
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    await session.commit()
    await session.refresh(student)
    return StudentResponse.model_validate(student)


async def get_student_modules_with_attendance_rate(session: AsyncSession, student_id: str):
    reg_result = await session.execute(select(ModuleRegistration).where(ModuleRegistration.student_id == student_id))
    registrations = reg_result.scalars().all()
    payload = []
    for registration in registrations:
        total_result = await session.execute(
            select(func.count(Attendance.attendance_id)).where(
                Attendance.student_id == student_id,
                Attendance.module_id == registration.module_id
            )
        )
        total = total_result.scalar() or 0
        present_result = await session.execute(
            select(func.count(Attendance.attendance_id)).where(
                Attendance.student_id == student_id,
                Attendance.module_id == registration.module_id,
                Attendance.attendance_status == 'PRESENT'
            )
        )
        present = present_result.scalar() or 0
        payload.append(
            {
                "module_id": registration.module_id,
                "attendance_rate": round(present / total * 100, 2) if total else 0.0,
            }
        )
    return payload


async def get_student_exam_eligibility_status(session: AsyncSession, student_id: str):
    result = await session.execute(select(Exam).where(Exam.student_id == student_id))
    rows = result.scalars().all()
    return [
        {
        "module_id": row.module_id, "attendance_rate": float(row.attendance_rate), "is_eligible": row.is_eligible
    } for row in rows]


async def _process_excel(session: AsyncSession, file_contents: bytes):
    workbook = openpyxl.load_workbook(io.BytesIO(file_contents))
    sheet = workbook.active

    successful = []
    failed = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or not row[0] or not row[1]:
            continue
        student_id = str(row[0]).strip()
        name = str(row[1]).strip()
        map_location = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        program_id = str(row[3]).strip() if len(row) > 3 and row[3] else None
        intake = str(row[4]).strip() if len(row) > 4 and row[4] else None

        # Check duplicates
        existing = await session.execute(
            select(Student).where(or_(Student.student_id == student_id, Student.name == name))
        )
        if existing.scalar():
            failed.append({"student_id": student_id, "name": name, "error": "User already exists"})
            continue

        new_student = Student(
            student_id=student_id,
            name=name,
            map_location=map_location,
            program_id=program_id,
            intake=int(intake),
        )
        session.add(new_student)
        successful.append({"student_id": student_id, "name": name, "map_location": map_location, "program_id": program_id, "intake": intake})

    await session.commit()
    return {"successful": successful, "failed": failed}


async def create_multiple_student_from_excel(session: AsyncSession, file_contents: bytes):
    return await _process_excel(session, file_contents)
