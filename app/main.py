from fastapi import FastAPI

from settings.config import settings
from routers import operation_check


app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    openapi_url=settings.openapi_url,
    docs_url=settings.docs_url,
    redoc_url=None,
)

app.include_router(operation_check.router, prefix=settings.prefix_url)