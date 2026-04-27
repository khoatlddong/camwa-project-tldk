from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.core.db import AsyncSessionDep
from backend.helpers.response_wrapper import ApiResponse
from backend.schemas.module_registration import ModuleRegistrationResponse, ModuleRegistrationCreate, \
    ModuleRegistrationUpdate
from backend.services import module_registration_service

router = APIRouter(
    prefix="/module-registrations",
    tags=["Module Registrations"]
)


@router.post("/create", response_model=ApiResponse[ModuleRegistrationResponse], status_code=201)
async def create_module_registration(session: AsyncSessionDep, data: ModuleRegistrationCreate):
    record = await module_registration_service.create_registration(session, data)
    return ApiResponse(
        message="Module registration created successfully",
        meta_data=record
    )


@router.get("/", response_model=ApiResponse[List[ModuleRegistrationResponse]])
async def get_all_module_registrations(session: AsyncSessionDep):
    records = await module_registration_service.get_all_registrations(session)
    return ApiResponse(
        message="Module registrations retrieved successfully",
        meta_data=records
    )


@router.get("/{module_reg_id}", response_model=ApiResponse[ModuleRegistrationResponse])
async def get_module_registration_by_id(session: AsyncSessionDep, module_reg_id: int):
    record = await module_registration_service.find_registration_by_id(session, module_reg_id)
    return ApiResponse(
        message="Module registration retrieved successfully",
        meta_data=record
    )


@router.put("/{module_reg_id}", response_model=ApiResponse[ModuleRegistrationResponse])
async def update_module_registration(session: AsyncSessionDep, module_reg_id: int, data: ModuleRegistrationUpdate):
    record = await module_registration_service.update_registration(session, module_reg_id, data)
    return ApiResponse(
        message="Module registration updated successfully",
        meta_data=record
    )


@router.delete("/{module_reg_id}", response_model=ApiResponse[None])
async def delete_module_registration(session: AsyncSessionDep, module_reg_id: int):
    await module_registration_service.delete_registration(session, module_reg_id)
    return ApiResponse(
        message="Module registration deleted successfully",
        meta_data=None
    )


@router.post("/create-from-excel", response_model=ApiResponse)
async def import_lecturers(session: AsyncSessionDep, file: UploadFile = File(...)):
    if not file.filename or not any(file.filename.lower().endswith(ext) for ext in [".xlsx", ".xls"]):
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files are allowed.")

    contents = await file.read()
    result = await module_registration_service.create_multiple_module_registration_from_excel(session, contents)
    return ApiResponse(
        message="Modules imported successfully",
        meta_data=result
    )