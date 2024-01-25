from logging import getLogger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dao.base import BaseDAO
from db.models import ShortLink

logger = getLogger(__name__)


class ShortLinksDAO(BaseDAO[ShortLink]):
    def __init__(self, session: AsyncSession):
        super().__init__(ShortLink, session)

    async def get_by_link_id(self, link_id: str) -> ShortLink | None:
        result = await self.session.execute(select(ShortLink).where(ShortLink.link_id == link_id))
        return result.scalar_one_or_none()
