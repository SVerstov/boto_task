import uvicorn
from fastapi import FastAPI, Request

from config import Config, setup_logger
from db.base import make_sessionmaker
from db.dao import DAO
from endpoints.short_links import router
from loguru import logger

app = FastAPI()
app.include_router(router)


@app.middleware("http")
async def add_dao_and_middleware(request: Request, call_next):
    """ Adds dao to request, wraps fastapi functions in a context manager.
    Get it like this: dao: HolderDao = request.state.dao
    """
    pool = make_sessionmaker(app.state.config.db)
    async with pool() as session:
        dao = DAO(session)
        request.state.dao = dao
        response = await call_next(request)
        await session.commit()
        return response


@app.middleware("http")
async def log_stuff(request: Request, call_next):
    logger_endpoints = logger.bind(name='endpoints')
    logger_endpoints.debug(f"{request.method} {request.url} from {request.client.host}")
    response = await call_next(request)
    logger_endpoints.debug(f"Response status code = {response.status_code}")
    return response


# @app.middleware("http")
# async def log_request(request: Request, call_next):
#     # Записываем информацию о запросе перед обработкой запроса
#     logger_endpoints = logger.bind(name='endpoints')
#     logger_endpoints.info({
#         "timestamp": request.headers.get("Date"),
#         "method": request.method,
#         "path": request.url.path,
#         "ip_address": request.client.host,
#     })
#
#     # Обработка запроса
#     response = await call_next(request)
#
#     # Дополнительная информация о запросе и ответе
#     logger_endpoints.info({
#         "status_code": response.status_code
#     })
#
#     return response


@app.on_event("startup")
def startup_event():
    setup_logger()
    config = Config()
    app.state.config = config


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
