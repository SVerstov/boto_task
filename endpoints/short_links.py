from fastapi import Request, Depends, HTTPException
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel

from config import Config
from db import ShortLink
from db.dao import DAO
from endpoints.utils import get_and_check_random_string, get_config, get_dao

router = APIRouter()


class LinkQuery(BaseModel):
    url: str
    status_code: int = 301


@router.post("/api/links/create")
async def create_new_link(
        request: Request,
        link_query: LinkQuery,
        config: Config = Depends(get_config),
        dao: DAO = Depends(get_dao),
):
    link_id = await get_and_check_random_string(dao, config.short_links.min_id_len)
    if not (300 <= link_query.status_code <= 308):
        raise HTTPException(status_code=400, detail="Invalid status code")
    new_link = ShortLink(
        full_link=link_query.url,
        link_id=link_id,
        created_by_ip=request.client.host,
        redirect_code=link_query.status_code,
    )
    dao.session.add(new_link)
    short_url = f'{config.short_links.base_url.rstrip("/")}/l/{new_link.link_id}'
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content={"short_url": short_url})


@router.get("/api/links/all")
async def get_all(dao: DAO = Depends(get_dao)):
    links = await dao.short_link.get_all()
    return [link.to_json() for link in links]


@router.delete("/l/{link_id}")
async def delete_link(link_id: str,
                      dao: DAO = Depends(get_dao)):
    is_deleted = bool(await dao.short_link.delete(ShortLink.link_id == link_id))
    if is_deleted:
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail="link doesn't exist")


@router.get("/l/{link_id}")
async def short_link_redirect(link_id: str,
                              dao: DAO = Depends(get_dao)):
    link_obj = await dao.short_link.get_by_link_id(link_id=link_id)
    if link_obj:
        link_obj.counter += 1
        return RedirectResponse(status_code=link_obj.redirect_code, url=link_obj.full_link)
    else:
        raise HTTPException(status_code=404, detail="Link not found")
