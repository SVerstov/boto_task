from fastapi import Request, Depends, HTTPException
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel, HttpUrl, field_validator

from config import Config
from db import ShortLink
from db.dao import DAO
from endpoints.utils import get_and_check_random_string, get_config, get_dao

router = APIRouter()
from loguru import logger


class LinkCreate(BaseModel):
    url: HttpUrl
    status_code: int = 301

    @field_validator('url')
    def convert_url_to_str(cls, value):
        if value:
            return str(value)

    @field_validator('status_code')
    def validate_status_code(cls, value):
        if isinstance(value, int) and not (300 <= value <= 308):
            raise ValueError('Invalid status code')
        return value


class LinkUpdate(LinkCreate):
    url: HttpUrl | None = None
    status_code: int | None = None


@router.post("/api/links/create")
async def create_new_link(
        request: Request,
        link_params: LinkCreate,
        config: Config = Depends(get_config),
        dao: DAO = Depends(get_dao),
):
    link_id = await get_and_check_random_string(dao, config.short_links.min_id_len)
    new_link = ShortLink(
        url=link_params.url,
        link_id=link_id,
        created_by_ip=request.client.host if request.client else None,
        status_code=link_params.status_code,
    )
    dao.session.add(new_link)
    logger.info(f"Created new link: {new_link}")
    short_url = f'{config.short_links.base_url.rstrip("/")}/{new_link.link_id}'
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"short_url": short_url})


@router.get("/api/links/all")
async def get_all(dao: DAO = Depends(get_dao)):
    links = await dao.short_link.get_all()
    return [link.to_json() for link in links]


@router.get("/api/links/{link_id}")
async def get_one(link_id: str, dao: DAO = Depends(get_dao)):
    link = await dao.short_link.get_by_link_id(link_id)
    return link.to_json()


@router.delete("/api/links/{link_id}")
async def delete_link(link_id: str, dao: DAO = Depends(get_dao)):
    is_deleted = bool(await dao.short_link.delete(ShortLink.link_id == link_id))
    if is_deleted:
        logger.info(f"Deleted link with id: {link_id}")
        return Response(status_code=204)
    else:
        raise HTTPException(status_code=404, detail="link doesn't exist")


@router.patch("/api/links/{link_id}")
async def patch_link(link_id: str, link_params: LinkUpdate, dao: DAO = Depends(get_dao)):
    count = await dao.short_link.update_records(ShortLink.link_id == link_id,
                                                **link_params.model_dump(exclude_none=True))
    if not count:
        raise HTTPException(status_code=404, detail="link doesn't exist")
    else:
        logger.info(f"Edited link with id: {link_id}")
        return Response(status_code=200)


@router.get("/{link_id}")
async def short_link_redirect(link_id: str, dao: DAO = Depends(get_dao)):
    link_obj = await dao.short_link.get_by_link_id(link_id=link_id)
    if link_obj:
        link_obj.counter += 1
        return RedirectResponse(status_code=link_obj.status_code, url=link_obj.url)
    else:
        raise HTTPException(status_code=404, detail="Link not found")
