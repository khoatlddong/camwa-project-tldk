from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException

from backend.services import excel_service

router = APIRouter(
    prefix="/excel",
    tags=["Excel"],
)

@router.post("/import/account/students")
async def import_student_accounts(
        file: UploadFile = File(...),
        background_task: BackgroundTasks = BackgroundTasks()
):
    if not file.filename.endswith((".xlsx", ".xls", "csv")):
        raise HTTPException(status_code=400, detail="Only .xlsx, .xls, and .csv files are allowed")

    file_bytes = await file.read()
    background_task.add_task(excel_service.import_student_account, file_bytes, file.filename)

    return {
        "message": "Important queued. Processing in background.",
    }