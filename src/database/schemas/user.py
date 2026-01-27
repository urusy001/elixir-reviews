from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    accepted_terms: bool = False
    blocked: bool = False


class UserCreate(BaseModel):
    id: int
    accepted_terms: bool = False
    blocked: bool = False


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    accepted_terms: bool | None = None
    blocked: bool | None = None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    accepted_terms: bool
    blocked: bool
