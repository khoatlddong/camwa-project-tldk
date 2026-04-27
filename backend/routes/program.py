from fastapi import APIRouter

from backend.core.db import AsyncSessionDep
from backend.helpers.response_wrapper import ApiResponse
from backend.schemas.program import ProgramResponse, ProgramCreate, ProgramUpdate
from backend.services import program_service

router = APIRouter(
    prefix="/program",
    tags=["Program"],
)


@router.post("/create", response_model=ApiResponse[ProgramResponse], status_code=201)
async def create_program(session: AsyncSessionDep, data: ProgramCreate):
    program = await program_service.create_program(session, data)
    return ApiResponse(
        message="Program created successfully",
        meta_data=program
    )


@router.get("/", response_model=ApiResponse[list[ProgramResponse]])
async def get_all_programs(session: AsyncSessionDep):
    programs = await program_service.get_all_programs(session)
    return ApiResponse(
        message="Programs retrieved successfully",
        meta_data=programs
    )


@router.get("/{program_id}", response_model=ApiResponse[ProgramResponse])
async def find_program_by_id(session: AsyncSessionDep, program_id: str):
    program = await program_service.find_program_by_id(session, program_id)
    return ApiResponse(
        message="Program retrieved successfully",
        meta_data=program
    )


@router.put("/{program_id}", response_model=ApiResponse[ProgramResponse])
async def update_program(session: AsyncSessionDep, program_id: str, data: ProgramUpdate):
    program = await program_service.update_program(session, program_id, data)
    return ApiResponse(
        message="Program updated successfully",
        meta_data=program
    )


@router.delete("/{program_id}", response_model=ApiResponse[None])
async def delete_program(session: AsyncSessionDep, program_id: str):
    await program_service.delete_program(session, program_id)
    return ApiResponse(
        message="Program deleted successfully",
        meta_data=None
    )


@router.get("/{program_id}/modules", response_model=ApiResponse)
async def view_modules_in_program(session: AsyncSessionDep, program_id: str):
    modules = await program_service.view_modules_in_program(session, program_id)
    return ApiResponse(
        message="Modules retrieved successfully",
        meta_data=modules
    )


@router.get("/{program_id}/lecturers", response_model=ApiResponse)
async def view_lecturers_in_program(session: AsyncSessionDep, program_id: str):
    lecturers = await program_service.view_lecturers_in_program(session, program_id)
    return ApiResponse(
        message="Lecturers retrieved successfully",
        meta_data=lecturers
    )


@router.get("/{program_id}/students", response_model=ApiResponse)
async def view_students_in_program(session: AsyncSessionDep, program_id: str):
    students = await program_service.view_students_in_program(session, program_id)
    return ApiResponse(
        message="Students retrieved successfully",
        meta_data=students
    )