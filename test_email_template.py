import asyncio

from backend.services.email_service import send_attendance_correction_notification, send_attendance_request_confirmation


test_email = "khoatld01@gmail.com"
test_id = 1

correction_data = {
    "module_id": "CS101",
    "original_status": "absent",
    "proposed_status": "present",
    "approved_status": "present",
    "reason": "I was in class but marked absent by mistake.",
}

# Data for attendance request confirmation
request_data = {
    "module_id": "CS101",
    "current_status": "absent",
    "proposed_status": "present",
    "reason": "I was in class but marked absent by mistake.",
}

async def main():
    print("Sending APPROVED correction notification...")
    result1 = await send_attendance_correction_notification(
        student_email=test_email,
        request_data=correction_data,
        is_approved=True,
        processed_by="Dr. Smith",
    )
    print("Approved result:", result1)

    print("\nSending REJECTED correction notification...")
    result2 = await send_attendance_correction_notification(
        student_email=test_email,
        request_data=correction_data,
        is_approved=False,
        processed_by="Dr. Ngoc",
    )
    print("Rejected result:", result2)

    print("\nSending attendance request confirmation...")
    result3 = await send_attendance_request_confirmation(
        student_email=test_email,
        request_data=request_data,
        request_id=test_id,
    )
    print("Confirmation result:", result3)

if __name__ == "__main__":
    asyncio.run(main())