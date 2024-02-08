# ruff: noqa: B008
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse, Response
from loguru import logger

from config import Config
from dao import DAO
from endpoints.utils import get_config, get_dao
from endpoints.validators import LinkCreate, LinkUpdate

links_router = APIRouter()


@links_router.post("/api/links/")
def create_new_link(
        link_params: LinkCreate,
        config: Config = Depends(get_config),
):
  with DAO(config) as dao:
    link_id = dao.links.create_short_link(
      link_len=config.short_links.id_len,
      **link_params.model_dump(exclude_none=True))

    logger.info(f"Created new link: {link_id} to {link_params.url}")
    short_url = f'{config.short_links.base_url.rstrip("/")}/{link_id}'
  return JSONResponse(status_code=status.HTTP_201_CREATED, content={"short_url": short_url})


@links_router.get("/api/links/")
async def get_all(config: Config = Depends(get_config)):
  with DAO(config) as dao:
    links = dao.links.get_many()
  return links


@links_router.get("/api/links/{link_id}")
async def get_one(link_id: str, config: Config = Depends(get_config)):
  with DAO(config) as dao:
    link = dao.links.get_by_link_id(link_id)
  if link:
    return link
  else:
    raise HTTPException(status_code=404, detail="Link not found")
#
#
# @links_router.delete("/api/links/{link_id}")
# async def delete_link(link_id: str, dao: DAO = Depends(get_dao)):
#   is_deleted = bool(await dao.short_link.delete(ShortLink.link_id == link_id))
#   if is_deleted:
#     logger.info(f"Deleted link with id: {link_id}")
#     return Response(status_code=204)
#   else:
#     raise HTTPException(status_code=404, detail="link doesn't exist")
#
#
# @links_router.patch("/api/links/{link_id}")
# async def patch_link(link_id: str, link_params: LinkUpdate, dao: DAO = Depends(get_dao)):
#   count = await dao.short_link.update_records(ShortLink.link_id == link_id, **link_params.model_dump(exclude_none=True))
#   if not count:
#     raise HTTPException(status_code=404, detail="link doesn't exist")
#   else:
#     logger.info(f"Edited link with id: {link_id}")
#     return Response(status_code=200)
#
#
# @links_router.get("/{link_id}")
# async def short_link_redirect(link_id: str, dao: DAO = Depends(get_dao)):
#   link_obj = await dao.short_link.get_by_link_id(link_id=link_id)
#   if link_obj:
#     link_obj.counter += 1
#     return RedirectResponse(status_code=link_obj.status_code, url=link_obj.url)
#   else:
#     raise HTTPException(status_code=404, detail="Link not found")
