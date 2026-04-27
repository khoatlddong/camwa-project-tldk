import io
from typing import List

import openpyxl
from fastapi import HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Module
from backend.schemas.module import ModuleResponse, ModuleCreate, ModuleUpdate


async def create_module(session: AsyncSession, data: ModuleCreate) -> ModuleResponse:
    module = Module(
        module_id=data.module_id,
        name=data.name,
        lecturer_id=data.lecturer_id,
        program_id=data.program_id,
        intake=data.intake,
        semester_id=data.semester_id,
        camera_path=data.camera_path,
    )
    session.add(module)
    await session.commit()
    await session.refresh(module)
    return ModuleResponse.model_validate(module)


async def view_modules(session: AsyncSession) -> List[ModuleResponse]:
    result = await session.execute(select(Module))
    modules = result.scalars().all()
    return [ModuleResponse.model_validate(module) for module in modules]


async def check_module_exists(session: AsyncSession, module_id: str) -> bool:
    return await session.get(Module, module_id) is not None


async def update_module(session: AsyncSession, module_id: str, data: ModuleUpdate) -> ModuleResponse:
    module = await session.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(module, field, value)
    await session.commit()
    await session.refresh(module)
    return ModuleResponse.model_validate(module)


async def delete_module(session: AsyncSession, module_id: str) -> None:
    module = await session.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    await session.delete(module)
    await session.commit()


async def _process_excel(session: AsyncSession, file_contents: bytes):
    workbook = openpyxl.load_workbook(io.BytesIO(file_contents))
    sheet = workbook.active

    successful = []
    failed = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        if not row or not row[0] or not row[1]:
            continue
        module_id = str(row[0]).strip()
        name = str(row[1]).strip()
        lecturer_id = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        program_id = str(row[3]).strip() if len(row) > 3 and row[3] else ""
        intake = str(row[4]).strip() if len(row) > 4 and row[4] else ""
        semester_id = str(row[5]).strip() if len(row) > 5 and row[5] else ""
        camera_path = str(row[6]).strip() if len(row) > 6 and row[6] else ""

        # Check duplicates
        existing = await session.execute(
            select(Module).where(or_(Module.module_id == module_id, Module.name == name))
        )
        if existing.scalar():
            failed.append({"module_id": module_id, "name": name, "error": "User already exists"})
            continue

        new_module = Module(
            module_id=module_id,
            name=name,
            lecturer_id=lecturer_id,
            program_id=program_id,
            intake=int(intake),
            semester_id=semester_id,
            camera_path=camera_path,
        )
        session.add(new_module)
        successful.append({"module_id": module_id, "name": name, "lecturer_id": lecturer_id, "program_id": program_id, "intake": intake, "semester_id": semester_id, "camera_path": camera_path})

    await session.commit()
    return {"successful": successful, "failed": failed}


async def create_multiple_module_from_excel(session: AsyncSession, file_contents: bytes):
    return await _process_excel(session, file_contents)
