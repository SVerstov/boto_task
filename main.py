import uvicorn
from fastapi import FastAPI, Request
from loguru import logger

from config import Config, setup_logger

from dao import DAO
from endpoints.short_links import links_router

app = FastAPI()
app.include_router(links_router)



@app.middleware("http")
async def log_stuff(request: Request, call_next):
  logger_endpoints = logger.bind(name="endpoints")
  logger_endpoints.debug(f"{request.method} {request.url}")
  response = await call_next(request)
  logger_endpoints.debug(f"Response status code = {response.status_code}")
  return response


@app.on_event("startup")
def startup_event():
  setup_logger()
  config = Config()
  DAO(config).init_tables()
  app.state.config = config


if __name__ == "__main__":
  uvicorn.run(app, host="127.0.0.1", port=5000)
