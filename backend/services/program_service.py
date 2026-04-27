from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Program, Student, Lecturer, Module
from backend.schemas.program import ProgramCreate, ProgramResponse, ProgramUpdate


async def create_program(session: AsyncSession, data: ProgramCreate) -> ProgramResponse:
    program = Program(
        program_id=data.program_id,
        name=data.name
    )
    session.add(program)
    await session.commit()
    await session.refresh(program)
    return ProgramResponse.model_validate(program)


async def get_all_programs(session: AsyncSession) -> List[ProgramResponse]:
    result = await session.execute(select(Program))
    programs = result.scalars().all()
    return [ProgramResponse.model_validate(program) for program in programs]


async def find_program_by_id(session: AsyncSession, program_id: str) -> ProgramResponse:
    program = await session.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    return ProgramResponse.model_validate(program)


async def delete_program(session: AsyncSession, program_id: str) -> None:
    program = await session.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")
    await session.delete(program)
    await session.commit()


async def update_program(session: AsyncSession, program_id: str, data: ProgramUpdate) -> ProgramResponse:
    program = await session.get(Program, program_id)
    if not program:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Program not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(program, field, value)

    await session.commit()
    await session.refresh(program)
    return ProgramResponse.model_validate(program)


async def assign_student_to_program(session: AsyncSession, program_id: str, student_id: str) -> None:
    student = await session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    student.program_id = program_id
    await session.commit()


async def assign_lecturer_to_program(session: AsyncSession, program_id: str, lecturer_id: str) -> None:
    lecturer = await session.get(Lecturer, lecturer_id)
    if not lecturer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")
    lecturer.program_id = program_id
    await session.commit()


async def assign_module_to_program(session: AsyncSession, program_id: str, module_id: str) -> None:
    module = await session.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    module.program_id = program_id
    await session.commit()


async def view_modules_in_program(session: AsyncSession, program_id: str) -> List[str]:
    result = await session.execute(select(Module.module_id).where(Module.program_id == program_id))
    return [module_id for (module_id,) in result.all()]


async def view_lecturers_in_program(session: AsyncSession, program_id: str) -> List[str]:
    result = await session.execute(select(Lecturer.lecturer_id).where(Lecturer.program_id == program_id))
    return [lecturer_id for (lecturer_id,) in result.all()]


async def view_students_in_program(session: AsyncSession, program_id: str) -> List[str]:
    result = await session.execute(select(Student.student_id).where(Student.program_id == program_id))
    return [student_id for (student_id,) in result.all()]