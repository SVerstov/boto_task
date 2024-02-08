# ruff: noqa: B008

from logging import getLogger

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse, Response

from src import dao
from src.config import Config
from src.endpoints.validators import LinkCreate

logger = getLogger(__name__)


def get_config(request: Request) -> Config:
  return request.app.state.config


links_router = APIRouter()


@links_router.post("/api/links/")
def create_new_link(
        link_params: LinkCreate,
        config: Config = Depends(get_config),
):
  with dao.get_conn(config.db_name) as conn:
    link_id = dao.create_link(conn,
                              config.id_len,
                              url=str(link_params.url),
                              status_code=link_params.status_code)
    logger.info(f"Created new link: {link_id} to {link_params.url}")
    short_url = f'{config.base_url.rstrip("/")}/{link_id}'
  return JSONResponse(status_code=status.HTTP_201_CREATED, content={"short_url": short_url})


@links_router.get("/api/links/")
def get_all(config: Config = Depends(get_config)):
  with dao.get_conn(config.db_name) as conn:
    return dao.get_all(conn)


@links_router.get("/api/links/{link_id}")
def get_one(link_id: str, config: Config = Depends(get_config)):
  with dao.get_conn(config.db_name) as conn:
    link = dao.get_by_link_id(conn, link_id)
  if link:
    return link
  else:
    raise HTTPException(status_code=404, detail="Link not found")


@links_router.delete("/api/links/{link_id}")
def delete_link(link_id: str, config: Config = Depends(get_config)):
  with dao.get_conn(config.db_name) as conn:
    is_deleted = bool(dao.delete_link(conn, link_id))
  if is_deleted:
    logger.info(f"Deleted link with id: {link_id}")
    return Response(status_code=204)
  else:
    raise HTTPException(status_code=404, detail="link doesn't exist")


@links_router.patch("/api/links/{link_id}")
def patch_link(link_id: str, link_params: LinkCreate, config: Config = Depends(get_config)):
  with dao.get_conn(config.db_name) as conn:
    count = dao.update_link(conn, link_id, url=str(link_params.url), status_code=link_params.status_code)
  if not count:
    raise HTTPException(status_code=404, detail="link doesn't exist")
  else:
    logger.info(f"Edited link with id: {link_id}")
    return Response(status_code=200)


@links_router.get("/{link_id}")
def short_link_redirect(link_id: str, config: Config = Depends(get_config)):
  with dao.get_conn(config.db_name) as conn:
    link = dao.get_by_link_id(conn, link_id)
    if link:
      dao.increase_counter(conn, link_id)
      return RedirectResponse(status_code=link["status_code"], url=link["url"])
    else:
      raise HTTPException(status_code=404, detail="Link not found")
