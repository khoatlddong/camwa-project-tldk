import asyncio
from backend.services.email_service import send_email

async def main():
    result = await send_email(
        to="khoatld01@gmail.com",
        subject="Test from FastAPI",
        text="This email was sent using aiosmtplib."
    )
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())