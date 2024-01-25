import random
import string

from fastapi import Request

from config import Config
from db import DAO, ShortLink


def get_random_string(length) -> str:
    symbols = string.ascii_letters + string.digits
    return ''.join(random.choice(symbols) for i in range(length))


async def get_and_check_random_string(dao: DAO, min_id_len: int) -> str:
    rnd_id = get_random_string(min_id_len)
    if await dao.short_link.count(ShortLink.link_id == rnd_id):
        await get_and_check_random_string(dao=dao, min_id_len=min_id_len + 1)
    return rnd_id



def get_config(request: Request) -> Config:
    return request.app.state.config


def get_dao(request: Request) -> DAO:
    return request.state.dao

