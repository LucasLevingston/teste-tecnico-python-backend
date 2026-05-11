from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference
from starlette.status import (
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from create_registro import criar_registro
from diagnostico import diagnostico_produtividade
from init_db import init_db
from models import DiagnosticoOut, RegistroOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="API de Foco e Produtividade",
    description="Registre blocos de trabalho e receba um diagnóstico inteligente de produtividade.",
    version="0.1.0",
    docs_url=None,  
    redoc_url=None,  
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


app.post(
    "/registro-foco",
    response_model=RegistroOut,
    status_code=201,
    summary="Registrar bloco de foco",
    tags=["registros"],
)(criar_registro)

app.get(
    "/diagnostico-produtividade",
    response_model=DiagnosticoOut,
    summary="Diagnóstico de produtividade",
    tags=["diagnostico"],
)(diagnostico_produtividade)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )