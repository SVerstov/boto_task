import random
import string

from fastapi import Request

from config import Config
from dao import DAO



def get_config(request: Request) -> Config:
    return request.app.state.config


async def get_dao(request: Request) -> DAO:
    return request.app.state.dao
