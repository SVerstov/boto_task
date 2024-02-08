import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request

from src.config import Config
from src import dao
from src.endpoints import links_router

logger = logging.getLogger()
from ecs_logging import StdlibFormatter as JSONFormatter

@asynccontextmanager
async def lifespan(app: FastAPI):
  from src.config import config
  init_logging(config)
  app.state.config = config
  with dao.get_conn(config.db_name) as conn:
    dao.setup_db(conn)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(links_router)


@app.middleware("http")
async def log_stuff(request: Request, call_next):
  logger.debug(f"{request.method} {request.url}")
  response = await call_next(request)
  logger.debug(f"Response status code = {response.status_code}")
  return response


def init_logging(config: Config):
  log_path = Path("logs")
  log_path.mkdir(exist_ok=True)
  logger.setLevel(config.log_level)
  stderr_handler = logging.StreamHandler()
  stderr_handler.setFormatter(
    logging.Formatter("[%(asctime)-10s] %(name)-8s [%(filename)s:%(lineno)s]: %(levelname)-6s %(message)s")
  )

  file_handler = logging.handlers.RotatingFileHandler(str(log_path / "boto.json.log"))
  file_handler.setFormatter(JSONFormatter())
  logger.addHandler(file_handler)


if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=8000)
