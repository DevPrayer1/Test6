from fastapi import FastAPI, Header, Depends, Response
from pydantic import BaseModel, field_validator
from typing import Annotated
from datetime import datetime
import re

app = FastAPI()


# -----------------------------------------------------------
# 1. Модель CommonHeaders — извлекает и валидирует заголовки
# -----------------------------------------------------------
class CommonHeaders(BaseModel):
    user_agent: str
    accept_language: str

    # Валидация формата Accept-Language (опциональная часть задания)
    @field_validator("accept_language")
    def validate_accept_language(cls, value):
        pattern = r"^[a-z]{2}-[A-Z]{2}(?:,[a-z]{2}(?:-[A-Z]{2})?(?:;q=\d\.\d)?)*$"
        if not re.match(pattern, value):
            raise ValueError(
                "Invalid Accept-Language format. Example: en-US,en;q=0.9,es;q=0.8"
            )
        return value


# Зависимость, извлекающая заголовки через Header()
def get_common_headers(
    user_agent: Annotated[str, Header(alias="User-Agent")],
    accept_language: Annotated[str, Header(alias="Accept-Language")],
) -> CommonHeaders:
    return CommonHeaders(
        user_agent=user_agent,
        accept_language=accept_language
    )


# -----------------------------------------------------------
# 2. Маршрут: GET /headers
# -----------------------------------------------------------
@app.get("/headers")
def read_headers(headers: CommonHeaders = Depends(get_common_headers)):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


# -----------------------------------------------------------
# 3. Маршрут: GET /info (добавляем заголовок ответа)
# -----------------------------------------------------------
@app.get("/info")
def read_info(
    response: Response,
    headers: CommonHeaders = Depends(get_common_headers)
):
    # Добавление заголовка ответа
    response.headers["X-Server-Time"] = datetime.utcnow().isoformat()

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }
