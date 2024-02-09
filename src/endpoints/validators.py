from typing import Any

from pydantic import BaseModel, HttpUrl, field_validator, model_validator


class LinkCreate(BaseModel):
  url: HttpUrl
  status_code: int = 301

  @field_validator("status_code")
  def validate_status_code(cls, value):
    if isinstance(value, int) and (301 <= value <= 308):
      return value
    err_msg = "Invalid status code"
    raise ValueError(err_msg)


