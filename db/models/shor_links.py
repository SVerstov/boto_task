from sqlalchemy import DateTime, text, Integer, BigInteger, Boolean, String, Date
from sqlalchemy.orm import Mapped, mapped_column as mc
from datetime import datetime, date
from db.base import Base


class ShortLink(Base):
    __tablename__ = "short_links"
    id: Mapped[int] = mc(Integer, primary_key=True)
    link_id: Mapped[str] = mc(index=True, unique=True)
    url: Mapped[str | None]
    created_by_ip: Mapped[str | None]
    created_at: Mapped[datetime] = mc(
        DateTime,
        default=datetime.now(),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    counter: Mapped[int] = mc(default=0)
    status_code: Mapped[int] = mc(default=301)

    def to_json(self):
        return {
            "id": self.id,
            "link_id": self.link_id,
            "url": self.url,
            "created_by_ip": self.created_by_ip,
            "created_at": self.created_at,
            "counter": self.counter,
            "status_code": self.status_code,
        }
