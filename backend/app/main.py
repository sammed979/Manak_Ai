import logging
import os
import sys
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from app.config.settings import settings
from app.api.v1.api import api_router

_LOG_FMT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format=_LOG_FMT,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("manak_ai")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=False,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": (
                    "An unexpected error occurred. Please try again later or contact support."
                )
            },
        )


@app.get("/", include_in_schema=False)
@app.head("/", include_in_schema=False)
async def root():
    payload = {
        "message": "MANAK AI - BIS Compliance Assistant",
        "version": settings.APP_VERSION,
        "status": "running",
        "demo_mode": settings.DEMO_MODE,
    }
    return JSONResponse(content=payload, status_code=200)


@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
async def health():
    return JSONResponse(content={"status": "healthy"}, status_code=200)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(
        content=(
            b"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
            b"<rect width='100' height='100' rx='20' fill='%230052cc'/>"
            b"<text x='50' y='70' text-anchor='middle' font-family='Arial,sans-serif' "
            b"font-size='52' font-weight='bold' fill='white'>M</text></svg>"
        ),
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=86400"},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG and os.getenv("RUN_MAIN") != "1",
    )
