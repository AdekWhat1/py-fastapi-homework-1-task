from datetime import date
from typing import Optional
from pydantic import ConfigDict, BaseModel


class MovieBase(BaseModel):
    name: str
    date: date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[date] = None
    score: Optional[float] = None
    genre: Optional[str] = None
    overview: Optional[str] = None
    crew: Optional[str] = None
    orig_title: Optional[str] = None
    status: Optional[str] = None
    orig_lang: Optional[str] = None
    budget: Optional[float] = None
    revenue: Optional[float] = None
    country: Optional[str] = None


class MovieResponse(MovieBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class MovieDetailResponseSchema(MovieResponse):
    pass


class MovieListResponseSchema(BaseModel):
    movies: list[MovieResponse]
    total_items: int
    total_pages: int
    prev_page: Optional[int] = None
    next_page: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
