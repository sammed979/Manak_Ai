import logging
import os
import re
import sys
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from app.config.settings import settings
from app.api.v1.api import api_router

_LOG_FMT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format=_LOG_FMT,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("manak_ai")


class PatternCORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware that supports glob-style wildcard origins (e.g.
    ``https://*.vercel.app``) combined with allow_credentials.

    The built-in starlette/fastapi CORSMiddleware will not echo back the
    request ``Origin`` header when the configured ``allow_origins`` list
    contains wildcards, because it only allows a literal ``"*"`` and that
    cannot be combined with ``Access-Control-Allow-Credentials: true``.

    This middleware replaces that behaviour: if an incoming Origin matches
    any pattern (either literally or via ``*`` glob) we echo the exact
    Origin back as the ``Access-Control-Allow-Origin`` header and mark
    ``Vary: Origin`` so downstream caches do the right thing.  Unknown
    origins are passed through unchanged so the standard CORSMiddleware or
    the router can still decide.
    """

    def __init__(self, app: ASGIApp, origins: list[str]):
        super().__init__(app)
        self._literal: set[str] = set()
        self._patterns: list[re.Pattern[str]] = []
        for raw in origins or []:
            origin = raw.strip().rstrip("/")
            if not origin:
                continue
            if "*" in origin:
                regex = re.escape(origin).replace(r"\*", r"[^./]+") + r"\Z"
                self._patterns.append(re.compile(regex, re.IGNORECASE))
            else:
                self._literal.add(origin.lower())

    def _matches(self, origin: str) -> bool:
        key = origin.rstrip("/").lower()
        if key in self._literal:
            return True
        for pattern in self._patterns:
            if pattern.match(key):
                return True
        return False

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        origin = request.headers.get("origin")
        if origin and self._matches(origin):
            if request.method == "OPTIONS":
                acrm = request.headers.get("access-control-request-method")
                headers = {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Credentials": "true",
                    "Vary": "Origin",
                    "Access-Control-Allow-Methods": acrm or "GET,POST,PUT,PATCH,DELETE,OPTIONS",
                    "Access-Control-Allow-Headers": request.headers.get(
                        "access-control-request-headers",
                        "Content-Type,Authorization,Accept,Accept-Language",
                    ),
                    "Access-Control-Max-Age": "86400",
                }
                return Response(status_code=204, headers=headers)
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            vary = response.headers.get("Vary")
            if vary:
                response.headers["Vary"] = vary + ", Origin"
            else:
                response.headers["Vary"] = "Origin"
            return response
        return await call_next(request)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=False,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Single CORS processor handles literal origins AND wildcard glob patterns
# (e.g. https://*.vercel.app) with allow_credentials=true.  Running ONE
# middleware avoids the standard CORSMiddleware overwriting our preflight
# 204 responses with 400 "Disallowed CORS origin" when the configured list
# contains wildcards (which the standard middleware rejects with credentials).
app.add_middleware(PatternCORSMiddleware, origins=list(settings.CORS_ORIGINS))

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
