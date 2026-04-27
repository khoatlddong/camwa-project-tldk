# import io
# from typing import List, Dict, Any
#
# from fastapi import status, HTTPException
# from openpyxl import Workbook
# from openpyxl.reader.excel import load_workbook
# from sqlalchemy import insert
#
# from backend.core.db import AsyncSessionLocal
# from backend.core.security import get_password_hash
# from backend.models import Iam
#
#
# async def import_student_account(file_bytes: bytes):
#     try:
#         wb = load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
#         ws = wb.active
#
#         header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
#         headers = [str(h).lower().strip() for h in header_row if h]
#         required = {"student_id", "email"}
#         missing = required - set(headers)
#         if missing:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Missing required headers: {missing}")
#
#         col_idx = {h: i for i, h in enumerate(headers)}
#         valid_rows, errors = [], []
#
#         for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
#             if not any(cell is not None for cell in row):
#                 continue
#
#             sid = str(row[col_idx["student_id"]]).strip() if row[col_idx["student_id"]] else None
#             email = str(row[col_idx["email"]]).strip() if row[col_idx["email"]] else None
#
#             if not sid or not email:
#                 errors.append(f"Row {row_idx}: Missing required fields for student ID {sid} or email {email}")
#
#
#             valid_rows.append({
#                 "iam_id": sid, "email": email, "role": "STUDENT"
#             })
#
#         wb.close()
#         return {"valid_rows": valid_rows, "errors": errors, "total_parsed": row_idx if "row_idx" in locals() else 0}
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(400, f"Excel parsing failed: {str(e)}")
#
#
# async def process_bulk_import(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
#     """Background task: validates, hashes passwords, bulk inserts via SQLAlchemy"""
#     async with AsyncSessionLocal() as db:
#         try:
#             parse_result = await self.parse_and_validate_students(file_bytes)
#             if not parse_result["valid_rows"]:
#                 return {"status": "completed", "inserted": 0, "errors": parse_result["errors"]}
#
#             # Prepare bulk data with hashed passwords
#             bulk_data = []
#             for row in parse_result["valid_rows"]:
#                 bulk_data.append({
#                     "iam_id": row["iam_id"],
#                     "username": row["username"],
#                     "email": row["email"],
#                     "password_hash": get_password_hash(row["password"]),
#                     "role": row["role"],
#                     "token_version": 1,
#                     "failed_attempts": 0,
#                     "locked_until": None
#                 })
#
#                 # PostgreSQL efficient bulk upsert
#             stmt = insert(Iam).values(bulk_data)
#             stmt = stmt.on_conflict_do_update(
#                 index_elements=["iam_id"],
#                 set_={
#                     "username": stmt.excluded.username,
#                     "email": stmt.excluded.email,
#                     "role": stmt.excluded.role
#                 }
#             )
#             await db.execute(stmt)
#             await db.commit()
#
#             return {
#                 "status": "completed",
#                 "inserted": len(bulk_data),
#                 "errors": parse_result["errors"][:50]
#             }
#         except Exception as e:
#             await db.rollback()
#             return {"status": "failed", "error": str(e), "inserted": 0}
#
#
#
# def export_students_to_excel(self, students: List[Dict[str, Any]]) -> bytes:
#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Students"
#
#     headers = ["Student ID", "Username", "Email", "Role", "Created At"]
#     ws.append(headers)
#
#     for cell in ws[1]:
#         cell.fill = self.header_fill
#         cell.font = self.header_font
#         cell.alignment = self.header_alignment
#         cell.border = self.thin_border
#
#     for s in students:
#         ws.append([
#             s.get("iam_id", ""),
#             s.get("username", ""),
#             s.get("email", ""),
#             s.get("role", ""),
#             s.get("created_at").strftime("%Y-%m-%d %H:%M:%S") if s.get("created_at") else ""
#         ])
#
#     self._apply_formatting(ws, len(students) + 1, len(headers))
#     return self._save_to_bytes(wb)
#
#
# def _save_to_bytes(self, wb: Workbook) -> bytes:
#     out = io.BytesIO()
#     wb.save(out)
#     out.seek(0)
#     return out.getvalue()