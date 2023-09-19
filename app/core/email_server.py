from typing import List

from email_validator import validate_email, EmailNotValidError
from fastapi import HTTPException
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr, BaseModel

from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL.USERNAME,
    MAIL_PASSWORD=settings.EMAIL.PASSWORD,
    MAIL_FROM=settings.EMAIL.FROM,
    MAIL_PORT=settings.EMAIL.PORT,
    MAIL_SERVER=settings.EMAIL.SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

mail_server = FastMail(conf)


class EmailSchema(BaseModel):
    emails: List[EmailStr]
    subject: str
    body: str


async def validate_email_format(email: EmailStr, check_deliverability: bool = True):
    try:
        validate_email(email, check_deliverability=check_deliverability)

    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def email_send(email: EmailSchema) -> None:
    message = MessageSchema(
        subject=email.subject,
        recipients=email.emails,
        body=email.body,
        subtype=MessageType.html)

    await mail_server.send_message(message)
