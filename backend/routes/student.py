from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.core.db import AsyncSessionDep
from backend.core.deps import AdminOrFA, AllAuthenticated
from backend.helpers.response_wrapper import ApiResponse
from backend.schemas.student import StudentResponse, StudentCreate, StudentUpdate
from backend.services import student_service

router = APIRouter(
    prefix="/student",
    tags=["Student"],
)


@router.post("/create", response_model=ApiResponse[StudentResponse], status_code=201)
async def create_student(session: AsyncSessionDep, data: StudentCreate, _: AdminOrFA = None):
    student = await student_service.create_student(session, data)
    return ApiResponse(
        message="Student created successfully",
        meta_data=student
    )


@router.get("/", response_model=ApiResponse[list[StudentResponse]])
async def get_all_students(session: AsyncSessionDep, _: AllAuthenticated = None):
    students = await student_service.get_all_students(session)
    return ApiResponse(
        message="Students retrieved successfully",
        meta_data=students
    )


@router.get("/{student_id}", response_model=ApiResponse[StudentResponse])
async def get_student_by_id(session: AsyncSessionDep, student_id: str):
    student = await student_service.find_student_by_id(session, student_id)
    return ApiResponse(
        message="Student retrieved successfully",
        meta_data=student
    )


@router.put("/{student_id}", response_model=ApiResponse[StudentResponse])
async def update_student(session: AsyncSessionDep, student_id: str, data: StudentUpdate):
    student = await student_service.update_student(session, student_id, data)
    return ApiResponse(
        message="Student updated successfully",
        meta_data=student
    )


@router.delete("/{student_id}", response_model=ApiResponse[None])
async def delete_student(session: AsyncSessionDep, student_id: str):
    await student_service.delete_student(session, student_id)
    return ApiResponse(
        message="Student deleted successfully",
        meta_data=None
    )


@router.post("/create-from-excel", response_model=ApiResponse)
async def import_students(session: AsyncSessionDep, file: UploadFile = File(...)):
    if not file.filename or not any(file.filename.lower().endswith(ext) for ext in [".xlsx", ".xls"]):
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files are allowed.")

    contents = await file.read()
    result = await student_service.create_multiple_student_from_excel(session, contents)
    return ApiResponse(
        message="Students imported successfully",
        meta_data=result
    )

