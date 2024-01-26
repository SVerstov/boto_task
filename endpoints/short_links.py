from fastapi import Request, Depends, HTTPException
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel

from config import Config
from db import ShortLink
from db.dao import DAO
from endpoints.utils import get_and_check_random_string, get_config, get_dao

router = APIRouter()


class LinkCreate(BaseModel):
    url: str
    status_code: int = 301


class LinkUpdate(BaseModel):
    url: str | None
    status_code: int | None


@router.post("/api/links/create")
async def create_new_link(
        request: Request,
        link_params: LinkCreate,
        config: Config = Depends(get_config),
        dao: DAO = Depends(get_dao),
):
    link_id = await get_and_check_random_string(dao, config.short_links.min_id_len)
    if not (300 <= link_params.status_code <= 308):
        raise HTTPException(status_code=400, detail="Invalid status code")
    new_link = ShortLink(
        url=link_params.url,
        link_id=link_id,
        created_by_ip=request.client.host if request.client else None,
        status_code=link_params.status_code,
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


@router.patch("/l/{link_id}")
async def patch_link(link_id: str,
                     link_params: LinkUpdate,
                     dao: DAO = Depends(get_dao)):
    if not (300 <= link_params.status_code <= 308):
        raise HTTPException(status_code=400, detail="Invalid status code")
    count = await dao.short_link.update_records(
        ShortLink.link_id == link_id,
        **link_params.model_dump()
    )
    if not count:
        raise HTTPException(status_code=404, detail="link doesn't exist")
    else:
        return Response(status_code=200)


@router.get("/l/{link_id}")
async def short_link_redirect(link_id: str,
                              dao: DAO = Depends(get_dao)):
    link_obj = await dao.short_link.get_by_link_id(link_id=link_id)
    if link_obj:
        link_obj.counter += 1
        return RedirectResponse(status_code=link_obj.status_code, url=link_obj.url)
    else:
        raise HTTPException(status_code=404, detail="Link not found")

