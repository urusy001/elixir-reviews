from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Gender = Literal["Не указан", "👨 Мужской", "👩 Женский"]


class SharedResultDraftBase(BaseModel):
    drugs: str | None = None
    age: int | None = Field(default=None, ge=0, le=150)
    gender: Gender = "Не указан"

    height: Decimal | None = Field(default=None, ge=Decimal("0"))
    starting_weight: Decimal | None = Field(default=None, ge=Decimal("0"))
    current_weight: Decimal | None = Field(default=None, ge=Decimal("0"))
    desired_weight: Decimal | None = Field(default=None, ge=Decimal("0"))
    lost_weight: Decimal | None = Field(default=None, ge=Decimal("0"))

    time_period: str | None = None
    course: str | None = None

    photo_url: str | None = None
    commentary: str | None = Field(default=None, max_length=2000)

    is_submitted: bool = False
    author: str | None = None


class SharedResultDraftCreate(SharedResultDraftBase):
    user_id: int


class SharedResultDraftUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drugs: str | None = None
    age: int | None = Field(default=None, ge=0, le=150)
    gender: Gender | None = None

    height: Decimal | None = Field(default=None, ge=Decimal("0"))
    starting_weight: Decimal | None = Field(default=None, ge=Decimal("0"))
    current_weight: Decimal | None = Field(default=None, ge=Decimal("0"))
    desired_weight: Decimal | None = Field(default=None, ge=Decimal("0"))
    lost_weight: Decimal | None = Field(default=None, ge=Decimal("0"))

    time_period: str | None = None
    course: str | None = None

    photo_url: str | None = None
    commentary: str | None = Field(default=None, max_length=2000)

    is_submitted: bool | None = None
    author: str | None = None


class SharedResultDraftRead(SharedResultDraftBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime