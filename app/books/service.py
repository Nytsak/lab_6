from app.books.repository import BookRepository
from app.books.models import Book
from app.books.schemas import BookRequest, BookStatus, SortOrder
from uuid import UUID
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

class BookService:
    def __init__(self, db: AsyncSession):
        self.repo = BookRepository(db)

    async def get_books(
        self,
        author: Optional[str] = None,
        status: Optional[BookStatus] = None,
        sort_by: Optional[str] = None,
        order: SortOrder = SortOrder.ASC,
        limit: int = 10,
        offset: int = 0
    ) -> Tuple[List[Book], int]:
        status_val = status.value if status else None
        items = await self.repo.get_all(
            author=author,
            status=status_val,
            sort_by=sort_by,
            order=order.value,
            limit=limit,
            offset=offset
        )
        total = await self.repo.count(author=author, status=status_val)
        return items, total

    async def get_book(self, book_id: UUID) -> Optional[Book]:
        return await self.repo.get_by_id(book_id)

    async def create_book(self, book_in: BookRequest) -> Book:
        new_book = Book(
            title=book_in.title,
            author=book_in.author,
            release_year=book_in.release_year,
            status=book_in.status.value,
            description=book_in.description
        )
        return await self.repo.add(new_book)

    async def delete_book(self, book_id: UUID) -> None:
        await self.repo.delete(book_id)
