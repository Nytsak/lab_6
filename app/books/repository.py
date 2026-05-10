from app.books.models import Book
from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc, func

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _build_query(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
    ):
        query = select(Book)

        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        if status:
            query = query.where(Book.status == status)

        if sort_by:
            sort_func = desc if order.lower() == "desc" else asc
            if sort_by == "title":
                query = query.order_by(sort_func(Book.title))
            elif sort_by == "release_year":
                query = query.order_by(sort_func(Book.release_year))
            elif sort_by == "author":
                query = query.order_by(sort_func(Book.author))
            elif sort_by == "id":
                query = query.order_by(sort_func(Book.id))

        return query

    async def count(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        query = select(func.count()).select_from(Book)
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        if status:
            query = query.where(Book.status == status)
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_all(
        self,
        author: Optional[str] = None,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        limit: int = 10,
        offset: int = 0
    ) -> List[Book]:
        query = self._build_query(author=author, status=status, sort_by=sort_by, order=order)
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, book_id: UUID) -> Optional[Book]:
        result = await self.db.execute(select(Book).where(Book.id == book_id))
        return result.scalars().first()

    async def add(self, book: Book) -> Book:
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete(self, book_id: UUID) -> None:
        book = await self.get_by_id(book_id)
        if book:
            await self.db.delete(book)
            await self.db.commit()
