import time
from contextlib import asynccontextmanager

import psutil
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import routers
from app.configs import get_appsettings, get_logger
from app.core.configs import LogConfig

logger = get_logger()

settings = get_appsettings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For activation of connections, creds and etc...
    yield


app = FastAPI(
    title=settings.appname.capitalize(),
    lifespan=lifespan,
    version=settings.appversion,
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}},
)


app.include_router(routers.recommends, prefix="/api/v1")


REQUEST_COUNT = Counter(
    "http_request_total", "Total HTTP Requests", ["method", "status", "path"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration",
    ["method", "status", "path"],
)
REQUEST_IN_PROGRESS = Gauge(
    "http_requests_in_progress", "HTTP Requests in progress", ["method", "path"]
)

# System metrics
CPU_USAGE = Gauge("process_cpu_usage", "Current CPU usage in percent")
MEMORY_USAGE = Gauge("process_memory_usage_bytes", "Current memory usage in bytes")


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    method = request.method
    path = request.url.path

    REQUEST_IN_PROGRESS.labels(method=method, path=path).inc()
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    status = response.status_code
    REQUEST_COUNT.labels(method=method, status=status, path=path).inc()
    REQUEST_LATENCY.labels(method=method, status=status, path=path).observe(duration)
    REQUEST_IN_PROGRESS.labels(method=method, path=path).dec()
    return response


def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.Process().memory_info().rss)


@app.get("/metrics")
async def metrics():
    update_system_metrics()
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


# @app.middleware("http")
# def db_session_middleware(request: Request, call_next):
#     try:
#         request.state.db_connection = MSSQLConnection(get_ms_sql_settings())
#         request.state.db = ReviewBIDataBase(request.state.db_connection)
#         response = call_next(request)
#     except DatabaseConnectionError as e:
#         logger.error(e)
#         raise RuntimeError(e) from e
#
#     return response


@app.get("/health", tags=["health check"])
def health():
    return JSONResponse(content={"status": "ok"}, status_code=200)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    logger.info("Starting web app...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=LogConfig,
        reload=False,
    )


if __name__ == "__main__":
    main()
