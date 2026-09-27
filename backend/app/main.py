import logging
import os
import sys
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    debug=False,  # Never expose FastAPI debug tracebacks; use our logging
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
    except Exception as exc:  # noqa: BLE001 - top-level safety net
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": (
                    "An unexpected error occurred. Please try again later or contact support."
                )
            },
        )


@app.get("/")
async def root():
    return {
        "message": "MANAK AI - BIS Compliance Assistant",
        "version": settings.APP_VERSION,
        "status": "running",
        "demo_mode": settings.DEMO_MODE,
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG and os.getenv("RUN_MAIN") != "1",
    )
