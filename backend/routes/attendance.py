from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status, BackgroundTasks, UploadFile, File

from backend.core.db import AsyncSessionDep
from backend.helpers.response_wrapper import ApiResponse
from backend.models.enums import RequestStatus
from backend.schemas.attendance import AttendanceResponse, AttendanceCreate, AttendanceUpdate, \
    AttendanceRequestResponse, AttendanceRequestCreate, CorrectionApproval, ExamEligibilityResponse
from backend.services import attendance_service

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
)

ALLOWED_EXCEL_EXTENSIONS = (".xlsx", ".xls")


def _validate_excel_upload(file: UploadFile) -> None:
    name = (file.filename or "").lower()
    if not name.endswith(ALLOWED_EXCEL_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .xlsx and .xls files are allowed",
        )


def _strip_exam_records(module_summary: Dict[str, Any]) -> Dict[str, Any]:
    """Remove non-serialisable ORM ``Exam`` instances from per-module summaries."""
    cleaned: Dict[str, Any] = {k: v for k, v in module_summary.items() if k != "results"}
    if "results" in module_summary:
        cleaned["results"] = [
            {k: v for k, v in entry.items() if k != "exam_record"}
            for entry in module_summary["results"]
        ]
    return cleaned


@router.post("/submit", response_model=ApiResponse[AttendanceResponse], status_code=201)
async def submit_attendance(
        session: AsyncSessionDep, data: AttendanceCreate
):
    attendance = await attendance_service.submit_attendance(session, data)
    return ApiResponse(
        message="Attendance submitted successfully",
        meta_data=attendance
    )


@router.get("/view", response_model=ApiResponse[List[AttendanceResponse]])
async def view_attendance(
        session: AsyncSessionDep, student_id: str, module_id: str
):
    if module_id:
        result = await attendance_service.view_by_module(session, module_id)
        return ApiResponse(
            message="Attendance retrieved successfully",
            meta_data=result
        )

    if student_id:
        result = await attendance_service.view_by_student(session, student_id)
        return ApiResponse(
            message="Attendance retrieved successfully",
            meta_data=result
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide either 'student_id' or 'module_id' query parameter")


@router.put("/{attendance_id}", response_model=ApiResponse[AttendanceResponse])
async def update_attendance(session: AsyncSessionDep, attendance_id: int, data: AttendanceUpdate):
    result = await attendance_service.update_attendance(session, attendance_id, data)
    return ApiResponse(
        message="Attendance updated successfully",
        meta_data=result,
    )


@router.delete("/{attendance_id}", response_model=ApiResponse[None])
async def delete_attendance(session: AsyncSessionDep, attendance_id: int):
    await attendance_service.delete_attendance(session, attendance_id)
    return ApiResponse(
        message="Attendance deleted successfully",
        meta_data=None
    )


@router.get("/requests", response_model=ApiResponse[List[AttendanceRequestResponse]])
async def get_attendance_requests(
    session: AsyncSessionDep,
    request_status: Optional[RequestStatus] = None,
    module_id: Optional[str] = None,
):
    rows = await attendance_service.get_request_by_status(
        session, request_status, module_id
    )
    return ApiResponse(
        message="Attendance requests retrieved successfully",
        meta_data=rows,
    )


@router.get(
    "/requests/student/{student_id}",
    response_model=ApiResponse[List[AttendanceRequestResponse]],
)
async def get_requests_by_student(session: AsyncSessionDep, student_id: str):
    rows = await attendance_service.view_attendance_requests_by_student(
        session, student_id
    )
    return ApiResponse(
        message="Attendance requests retrieved successfully",
        meta_data=rows,
    )


@router.get(
    "/requests/module/{module_id}",
    response_model=ApiResponse[List[AttendanceRequestResponse]],
)
async def get_requests_by_module(session: AsyncSessionDep, module_id: str):
    rows = await attendance_service.view_attendance_requests_by_module(
        session, module_id
    )
    return ApiResponse(
        message="Attendance requests retrieved successfully",
        meta_data=rows,
    )



@router.post("/request-correction", response_model=ApiResponse[AttendanceRequestResponse], status_code=201)
async def request_correction(session: AsyncSessionDep, background_task: BackgroundTasks, data: AttendanceRequestCreate):
    result = await attendance_service.request_correction(session, background_task, data)
    return ApiResponse(
        message="Correction request submitted successfully",
        meta_data=result
    )


@router.put("/correction/{request_id}", response_model=ApiResponse[dict])
async def handle_correction(session: AsyncSessionDep, request_id: int, approval: CorrectionApproval, background_task: BackgroundTasks):
    result = await attendance_service.handle_correction(session, background_task, request_id, approval)
    return ApiResponse(
        message="Correction request handled successfully",
        meta_data=result
    )


@router.delete("/requests/{request_id}", response_model=ApiResponse[None])
async def delete_attendance_request(session: AsyncSessionDep, request_id: int):
    await attendance_service.delete_attendance_request(session, request_id)
    return ApiResponse(
        message="Attendance request deleted successfully",
        meta_data=None,
    )


@router.post("/import/excel", response_model=ApiResponse[dict])
async def import_attendance_from_excel(session: AsyncSessionDep, file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only .xlsx and .xls files are allowed")

    file_bytes = await file.read()
    result = await attendance_service.import_attendance_from_excel(session, file_bytes)

    return ApiResponse(
        message="Attendance imported successfully",
        meta_data={
            "successful": len(result.get("successful", [])),
            "failed": len(result.get("failed", [])),
            "errors": result.get("errors", [])
        }
    )


@router.get(
    "/exam-eligibility",
    response_model=ApiResponse[List[ExamEligibilityResponse]],
)
async def get_exam_eligibility(
    session: AsyncSessionDep,
    student_id: Optional[str] = None,
    module_id: Optional[str] = None,
):
    if module_id:
        records = await attendance_service.get_exam_eligibility_by_module(
            session, module_id
        )
        return ApiResponse(
            message="Exam eligibility retrieved successfully",
            meta_data=records,
        )
    if student_id:
        records = await attendance_service.get_exam_eligibility_by_student(
            session, student_id
        )
        return ApiResponse(
            message="Exam eligibility retrieved successfully",
            meta_data=records,
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Provide either 'student_id' or 'module_id' query parameter",
    )


@router.get(
    "/exam-eligibility/check",
    response_model=ApiResponse[Dict[str, Any]],
)
async def check_exam_eligibility(
    session: AsyncSessionDep, student_id: str, module_id: str
):
    result = await attendance_service.check_exam_eligibility(
        session, student_id, module_id
    )
    exam_record = result.get("exam_record")
    if hasattr(exam_record, "exam_id"):
        result["exam_record"] = ExamEligibilityResponse.model_validate(
            exam_record
        ).model_dump()
    return ApiResponse(
        message="Exam eligibility checked successfully",
        meta_data=result,
    )


@router.post(
    "/exam-eligibility/module/{module_id}",
    response_model=ApiResponse[List[Dict[str, Any]]],
)
async def update_exam_eligibility_for_module(
    session: AsyncSessionDep, module_id: str
):
    results = await attendance_service.update_eligibility_for_module(
        session, module_id
    )
    return ApiResponse(
        message="Exam eligibility updated successfully",
        meta_data=[
            {k: v for k, v in entry.items() if k != "exam_record"}
            for entry in results
        ],
    )


@router.post(
    "/exam-eligibility/update-all-modules",
    response_model=ApiResponse[Dict[str, Any]],
)
async def update_exam_eligibility_for_all_modules(session: AsyncSessionDep):
    data = await attendance_service.update_exam_eligibility_for_all_modules(session)
    return ApiResponse(
        message="Exam eligibility updated for all modules",
        meta_data={
            "summary": data["summary"],
            "modules": [_strip_exam_records(m) for m in data["modules"]],
        },
    )


@router.post(
    "/exam-eligibility/lecturer/{lecturer_id}/update",
    response_model=ApiResponse[Dict[str, Any]],
)
async def update_exam_eligibility_for_lecturer(
    session: AsyncSessionDep, lecturer_id: str
):
    data = await attendance_service.update_exam_eligibility_for_lecturer_modules(
        session, lecturer_id
    )
    return ApiResponse(
        message="Exam eligibility updated for lecturer's modules",
        meta_data={
            "lecturer_id": data["lecturer_id"],
            "summary": data["summary"],
            "modules": [_strip_exam_records(m) for m in data["modules"]],
        },
    )


@router.post(
    "/exam-eligibility/export",
    response_model=ApiResponse[Dict[str, Any]],
)
async def export_exam_eligibility(session: AsyncSessionDep):
    result = await attendance_service.export_exam_eligibility_to_excel(session)
    return ApiResponse(
        message="Exam eligibility exported successfully",
        meta_data=result,
    )


@router.post(
    "/exam-eligibility/lecturer/{lecturer_id}/export",
    response_model=ApiResponse[Dict[str, Any]],
)
async def export_exam_eligibility_for_lecturer(
    session: AsyncSessionDep, lecturer_id: str
):
    result = await attendance_service.export_exam_eligibility_for_lecturer_to_excel(
        session, lecturer_id
    )
    return ApiResponse(
        message="Exam eligibility exported for lecturer's modules",
        meta_data=result,
    )