from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from loguru import logger

from src import dao
from src.endpoints import links_router


@asynccontextmanager
async def lifespan(app: FastAPI):
  from config import config
  app.state.config = config
  with dao.get_conn(config.db_name) as conn:
    dao.setup_db(conn)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(links_router)


@app.middleware("http")
async def log_stuff(request: Request, call_next):
  logger_endpoints = logger.bind(name="endpoints")
  logger_endpoints.debug(f"{request.method} {request.url}")
  response = await call_next(request)
  logger_endpoints.debug(f"Response status code = {response.status_code}")
  return response


if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=8000)
