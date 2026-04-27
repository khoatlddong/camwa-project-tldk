from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.core.db import AsyncSessionDep
from backend.helpers.response_wrapper import ApiResponse
from backend.schemas.module import ModuleResponse, ModuleCreate, ModuleUpdate
from backend.services import module_service

router = APIRouter(
    prefix="/module",
    tags=["Module"],
)


@router.post("/create", response_model=ApiResponse[ModuleResponse], status_code=201)
async def create_module(session: AsyncSessionDep, data: ModuleCreate):
    module = await module_service.create_module(session, data)
    return ApiResponse(
        message="Module created successfully",
        meta_data=module
    )


@router.get("/", response_model=ApiResponse[List[ModuleResponse]])
async def view_modules(session: AsyncSessionDep):
    modules = await module_service.view_modules(session)
    return ApiResponse(
        message="Modules retrieved successfully",
        meta_data=modules
    )


@router.put("/{module_id}", response_model=ApiResponse[ModuleResponse])
async def update_module(session: AsyncSessionDep, module_id: str, data: ModuleUpdate):
    module = await module_service.update_module(session, module_id, data)
    return ApiResponse(
        message="Module updated successfully",
        meta_data=module
    )


@router.delete("/{module_id}", response_model=ApiResponse[None])
async def delete_module(session: AsyncSessionDep, module_id: str):
    await module_service.delete_module(session, module_id)
    return ApiResponse(
        message="Module deleted successfully",
        meta_data=None
    )


@router.post("/create-from-excel", response_model=ApiResponse)
async def import_lecturers(session: AsyncSessionDep, file: UploadFile = File(...)):
    if not file.filename or not any(file.filename.lower().endswith(ext) for ext in [".xlsx", ".xls"]):
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files are allowed.")

    contents = await file.read()
    result = await module_service.create_multiple_module_from_excel(session, contents)
    return ApiResponse(
        message="Modules imported successfully",
        meta_data=result
    )