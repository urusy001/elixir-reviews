from pydantic import BaseModel, ConfigDict, Field


class ProductFeatureBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    price: float
    balance: int


class ProductBase(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    name: str
    onec_id: str = Field(..., alias="onec_id")
    url: str
    image: str
    features: list[ProductFeatureBase]


class ProductSearchResultBase(BaseModel):
    model_config = ConfigDict(extra="ignore")

    items: list[ProductBase]
    total: int


class ProductFeatureRead(ProductFeatureBase):
    model_config = ConfigDict(extra="ignore")


class ProductRead(ProductBase):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    description: str | None = None
    images: list[str] = Field(default_factory=list)


class ProductSearchResultRead(ProductSearchResultBase):
    model_config = ConfigDict(extra="ignore")

    items: list[ProductRead]
    total: int