from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.database.session import get_db
from src.database.models import MovieModel
from src.schemas.movies import (
    MovieCreate,
    MovieUpdate,
    MovieResponse,
    MovieListResponseSchema,
    MovieDetailResponseSchema
)

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.get("/", response_model=MovieListResponseSchema)
async def get_movies(
        page: int = Query(1, ge=1),
        per_page: int = Query(10, ge=1, le=20),
        db: AsyncSession = Depends(get_db)
):
    total_items = await db.scalar(select(func.count()).select_from(MovieModel))
    if not total_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    total_pages = (total_items + per_page - 1) // per_page
    if page > total_pages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No movies found."
        )

    offset = (page - 1) * per_page
    result = await db.execute(select(MovieModel).offset(offset).limit(per_page))
    movies = result.scalars().all()

    prev_page = f"/theater/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None
    next_page = f"/theater/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None

    return {
        "movies": movies,
        "total_items": total_items,
        "total_pages": total_pages,
        "prev_page": prev_page,
        "next_page": next_page
    }


@router.get("/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found."
        )
    return movie


@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(body: MovieCreate, db: AsyncSession = Depends(get_db)):
    new_movie = MovieModel(**body.model_dump())
    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)
    return new_movie


@router.patch("/{movie_id}/", response_model=MovieResponse)
async def update_movie(movie_id: int, body: MovieUpdate, db: AsyncSession = Depends(get_db)):
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found."
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(movie, key, value)

    await db.commit()
    await db.refresh(movie)
    return movie


@router.delete("/{movie_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    movie = await db.get(MovieModel, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie with the given ID was not found."
        )

    await db.delete(movie)
    await db.commit()
    return None
