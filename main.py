import uvicorn
from fastapi import FastAPI, Request

from config import Config, setup_logger
from db.base import make_sessionmaker
from db.dao import DAO
from endpoints.short_links import router

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


@app.on_event("startup")
def startup_event():
    config = Config()
    app.state.config = config


if __name__ == '__main__':
    setup_logger()
    uvicorn.run(app, host="0.0.0.0", port=5000)
