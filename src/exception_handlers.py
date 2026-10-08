from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from exceptions import DuplicatesIdempotencyKeyError, ResourceNotExistError, UnauthorizeError


def create_exception_handlers(app: FastAPI) -> None:
    """Регистрация обработчиков ошибок."""

    @app.exception_handler(ResourceNotExistError)
    async def message_404(_: Request, exc: ResourceNotExistError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, detail={"message": exc})

    @app.exception_handler(UnauthorizeError)
    async def message_401(_: Request, exc: UnauthorizeError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": exc})

    @app.exception_handler(DuplicatesIdempotencyKeyError)
    async def message_409(_: Request, exc: DuplicatesIdempotencyKeyError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": exc})
