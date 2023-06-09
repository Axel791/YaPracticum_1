from app.schemas.genres import Genre
from app.services.genre import genre_service, GenreService

router = APIRouter()


@router.get('/get/{genre_id}')
async def get_genre(
        genre_id: str,
        genre_service: GenreService = Depends(genre_service)
) -> Genre:
    return await genre_service.get(genre_id=genre_id)
