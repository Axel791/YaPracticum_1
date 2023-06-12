from fastapi import APIRouter, Depends

from typing import List, Optional

from app.core.config import settings
from app.schemas.films import FilmWork
from app.services.film import film_service, FilmWorkService

router = APIRouter()


@router.get('/get/{film_id}')
async def get_film(
        film_id: str,
        film_work_service: FilmWorkService = Depends(film_service)
) -> FilmWork:
    return await film_work_service.get(film_id=film_id)


@router.get('/list')
async def list_films(
        genres: Optional[str] = None,
        rating_order: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = settings.DEFAULT_PAGE_SIZE,
        film_work_service: FilmWorkService = Depends(film_service)
) -> List[FilmWork]:
    return await film_work_service.list(genre=genres, rating_order=rating_order,
                                        page=page, page_size=page_size)


@router.get('/search/{query}')
async def list_films(
        query: str,
        page: Optional[int] = 1,
        page_size: Optional[int] = settings.DEFAULT_PAGE_SIZE,
        film_work_service: FilmWorkService = Depends(film_service)
) -> List[FilmWork]:
    return await film_work_service.search(query=query, page=page, page_size=page_size)
