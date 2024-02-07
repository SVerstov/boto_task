from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator, model_validator


class LinkCreate(BaseModel):
  url: HttpUrl
  status_code: int = 301

  @field_validator("url")
  def convert_url_to_str(cls, value):
    if value:
      return str(value)

  @field_validator("status_code")
  def validate_status_code(cls, value):
    if isinstance(value, int) and (301 <= value <= 308):
      return value
    err_msg = "Invalid status code"
    raise ValueError(err_msg)


class LinkUpdate(LinkCreate):
  url: HttpUrl | None = None
  status_code: int | None = None

  @model_validator(mode="before")
  @classmethod
  def has_at_least_1_param(cls, data: Any) -> Any:
    assert isinstance(data, dict)
    assert data.get("url") or data.get("status_code")
    return data
