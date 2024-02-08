from pathlib import Path

from config.structures import ConfigBase, ConfigBranch


class ShortLinksConfig(ConfigBranch):
  id_len: int
  base_url: str


class DBConfig(ConfigBranch):
  path: str


class Config(ConfigBase):
  """Connect config branches (class from ConfigBranch) here"""

  db: DBConfig
  short_links: ShortLinksConfig
