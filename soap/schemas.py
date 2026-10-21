from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, examples=["Clean Code"])
    author: str = Field(min_length=1, examples=["Robert C. Martin"])
    available_copies: int = Field(ge=0, examples=[5])
    rental_price: float = Field(ge=0, examples=[3.5])


class BookCreate(BookBase):
    id: int = Field(gt=0, examples=[1])


class BookUpdate(BookBase):
    pass


class BookOut(BookCreate):
    model_config = ConfigDict(from_attributes=True)