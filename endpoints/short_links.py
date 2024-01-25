from fastapi import Request, Depends, HTTPException
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from config import Config
from db import ShortLink
# from db import News
from db.dao import DAO
from endpoints.utils import get_and_check_random_string, get_config, get_dao

router = APIRouter()


class Link(BaseModel):
    url: str


@router.post("/api/links/generate")
async def short_link(
        request: Request,
        link: Link,
        config: Config = Depends(get_config),
        dao: DAO = Depends(get_dao)):
    link_id = await get_and_check_random_string(dao, config.short_links.min_id_len)
    new_link = ShortLink(
        full_link=link.url,
        link_id=link_id,
        created_by_ip=request.client.host
    )
    dao.session.add(new_link)
    short_url = f'{config.short_links.base_url.rstrip("/")}/l/{new_link.link_id}'
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={"short_url": short_url})


@router.get("/l/{link_id}")
async def short_link_redirect(link_id: str,
                              dao: DAO = Depends(get_dao)):
    link_obj = await dao.short_link.get_by_link_id(link_id=link_id)
    if link_obj:
        link_obj.counter += 1
        return RedirectResponse(status_code=301, url=link_obj.full_link)
    else:
        HTTPException(status_code=404, detail="Link not found")


@router.get("/api/links/all")
async def read_root(dao: DAO = Depends(get_dao)):
    links = await dao.short_link.get_all()
    return [link.to_json() for link in links]
