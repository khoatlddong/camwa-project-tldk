import asyncio
import os
from datetime import datetime
from email.message import EmailMessage
from typing import Optional, Any

from aiosmtplib import SMTP

from backend.core.configs import settings

RETRY_ATTEMPTS = int(os.environ.get("EMAIL_RETRY_ATTEMPTS", 3))


async def send_email(*, to: str, subject: str, text: str, html: Optional[str] = None) -> dict[str, Any]:

    msg = EmailMessage()
    msg["From"] = settings.MAIL_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")


    last_error = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            async with SMTP(
                hostname=settings.MAIL_SERVER,
                port=settings.MAIL_PORT,
                use_tls=settings.MAIL_SSL_TLS,
                start_tls=settings.MAIL_STARTTLS,
            ) as smtp:
                await smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
                await smtp.send_message(msg)

            return {"success": True, "message": "Email sent successfully", "attempt": attempt}
        except Exception as e:
            last_error = e
            if attempt < RETRY_ATTEMPTS:
                delay = min(2 ** (attempt - 1), 5)
                await asyncio.sleep(delay)

    raise RuntimeError(f"Failed to send email after {RETRY_ATTEMPTS} attempts: {last_error}")


async def send_attendance_correction_notification(
    student_email: str,
    request_data: dict[str, Any],
    is_approved: bool,
    processed_by: str,
) -> dict[str, Any]:
    status = "Approved" if is_approved else "Rejected"
    status_color = "#28a745" if is_approved else "#dc3545"
    final_status_label = "Approved" if is_approved else "Final"

    subject = f"Attendance Correction Request {status}"
    text = f"""
Dear Student,

Your attendance correction request has been {status.lower()}.

Request Details:
- Module ID: {request_data.get("module_id")}
- Original Status: {request_data.get("original_status", "N/A")}
- Requested Status: {request_data.get("proposed_status")}
- {final_status_label} Status: {request_data.get("approved_status") or request_data.get("proposed_status")}
- Reason: {request_data.get("reason", "No reason provided")}
- Processed by: {processed_by}
- Processed at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Best regards,
CAMWA System
""".strip()

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {status_color}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; border: 1px solid #ddd; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Attendance Correction Request - {status}</h2>
        </div>
        <div class="content">
            <p>Module ID: {request_data.get("module_id")}</p>
            <p>Requested Status: {request_data.get("proposed_status")}</p>
            <p>Processed by: {processed_by}</p>
        </div>
    </div>
</body>
</html>
""".strip()

    return await send_email(to=student_email, subject=subject, text=text, html=html)


async def send_attendance_request_confirmation(
    student_email: str,
    request_data: dict[str, Any],
    request_id: int,
) -> dict[str, Any]:
    subject = "Attendance Correction Request Submitted Successfully"
    text = f"""
Dear Student,

Your attendance correction request has been submitted and is pending review.

Request Details:
- Request ID: {request_id}
- Module ID: {request_data.get("module_id")}
- Current Status: {request_data.get("current_status", "N/A")}
- Requested Status: {request_data.get("proposed_status")}
- Reason: {request_data.get("reason", "No reason provided")}
- Submitted at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Best regards,
CAMWA System
""".strip()

    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Attendance Correction Request Submitted</h2>
    <p><strong>Request ID:</strong> #{request_id}</p>
    <p><strong>Module ID:</strong> {request_data.get("module_id")}</p>
    <p><strong>Requested Status:</strong> {request_data.get("proposed_status")}</p>
</body>
</html>
""".strip()

    return await send_email(to=student_email, subject=subject, text=text, html=html)

