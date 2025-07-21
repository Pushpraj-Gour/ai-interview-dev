import asyncio
from contextlib import asynccontextmanager
import traceback

import uvicorn
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Query, Request,
                     status)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api import project_api
from contextlib import asynccontextmanager
from app.db.database import engine, Base

import logging
logging.basicConfig(format='%(asctime)s: %(levelname)s: [%(funcName)s]: %(message)s', level=logging.INFO, force=True)

from app.config import keys

app_name = ''
routers = []
if keys.routers == 'data_gathering':
    routers = [project_api.router]
    app_name = 'Interview APIs'

else:
    routers = [project_api.router]
    app_name = 'Juice Creativity - All APIs'

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown (optional)
    # cleanup code here if needed

app = FastAPI(title=app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can lock this down later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix=keys.api_prefix)
for router in routers:
    api_router.include_router(router)
app.include_router(api_router)


def exception_error_handler_500(request, exc):
    if isinstance(exc, ExceptionGroup):
        return JSONResponse({'detail': ''.join(traceback.TracebackException.from_exception(exc.exceptions[0]).format())}, 500)
    else:
        return JSONResponse({'detail': ''.join(traceback.TracebackException.from_exception(exc).format())}, 500)

def exception_error_handler_400(request, exc):
    if isinstance(exc, ExceptionGroup):
        return JSONResponse({'detail': ''.join(traceback.TracebackException.from_exception(exc.exceptions[0]).format())}, 400)
    else:
        return JSONResponse({'detail': ''.join(traceback.TracebackException.from_exception(exc).format())}, 400)

def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


app.add_exception_handler(RequestValidationError, validation_exception_handler) # type: ignore
app.add_exception_handler(ValueError, exception_error_handler_400)
app.add_exception_handler(RuntimeError, exception_error_handler_500)
app.add_exception_handler(Exception, exception_error_handler_500)

@app.get('/')
def health_check():
    return "OK"

@app.get('/ping')
def ping():
    return "PONG!"

@app.post('/ping')
def ping2():
    return "PONG!"

@app.post('/sleep/{seconds}/{caller}')
async def sleep(seconds: int, caller: str):
	logging.info(f'Sleeping for {seconds} seconds, called by {caller}')
	await asyncio.sleep(seconds)

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8081)