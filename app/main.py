import time

from fastapi import FastAPI, Request
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.configs import LogConfig, get_logger
from app.api import v1


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    request.state.logger = get_logger()
    request.state.logger.info(f'{start_time=}')

    # await check_exist(request)
    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    request.state.logger.info(f'{process_time=}')
    return response


app.include_router(v1.auth, prefix='/api/v1')
app.include_router(v1.items, prefix='/api/v1')
app.include_router(v1.jokes, prefix='/api/v1')
app.include_router(v1.namespace, prefix='/api/v1')


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000, log_config=LogConfig, reload=True)
