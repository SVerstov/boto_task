from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
  id_len: int
  base_url: str
  db_name: str | Path
  log_level: str = "INFO"


config = Config(
  id_len=5,
  base_url="http://127.0.0.1:8000",
  db_name="db.sqlite",
  log_level="DEBUG"
)
