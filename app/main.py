import time
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from app.api import v1
from app.configs import LogConfig, get_logger


def fake_answer_to_everything_ml_model(x: float):
    return x * 42


ml_models = {}


# For more description see: https://asgi.readthedocs.io/en/latest/specs/lifespan.html
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()


# Custom Docs: https://fastapi.tiangolo.com/how-to/custom-docs-ui-assets/
app = FastAPI(lifespan=lifespan)
sub_app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    request.state.logger = get_logger()
    request.state.logger.info(f"{start_time=}")

    # await check_exist(request)
    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    request.state.logger.info(f"{process_time=}")
    return response


@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    return {"result": result}


# If task is defined as async and inside the sync code, you must use the run_in_threadpool
def write_notification(email: str, message=""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}


templates = Jinja2Templates(directory="app/templates")


@sub_app.get("/static/{path}", response_class=HTMLResponse)
def static_files(path: str):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": path,
            "title": "Demo",
            "body_content": "This is the demo for using FastAPI with Jinja templates",
        },
    )


# Add another the single webserver
# by default return 307 Temporary Redirect
app.mount("/static", WSGIMiddleware(sub_app), name="static")


app.include_router(v1.auth, prefix="/api/v1")
app.include_router(v1.items, prefix="/api/v1")
app.include_router(v1.jokes, prefix="/api/v1")
app.include_router(v1.namespace, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=LogConfig, reload=True)
