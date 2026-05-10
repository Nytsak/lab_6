from fastapi import APIRouter, HTTPException, status, Query, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.utils import generate_pagination_links
from app.auth.models import User
from app.books.schemas import BookRequest, BookResponse, BookStatus, SortOrder, PaginatedBooksResponse
from app.books.service import BookService
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/api", tags=["Books"])

@router.get("/books", response_model=PaginatedBooksResponse)
async def get_all_books(
    request: Request,
    sort_by: Optional[str] = None,
    order: SortOrder = SortOrder.ASC,
    author: Optional[str] = None,
    status: Optional[BookStatus] = None,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = BookService(db)
    items, total = await service.get_books(
        sort_by=sort_by, order=order,
        author=author, status=status,
        limit=limit, offset=offset
    )

    pagination = generate_pagination_links(request, total, limit, offset)

    return PaginatedBooksResponse(
        total=total,
        limit=limit,
        offset=offset,
        next_page=pagination["next_page"],
        prev_page=pagination["prev_page"],
        items=items,
    )

@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = BookService(db)
    book = await service.get_book(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book

@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = BookService(db)
    return await service.create_book(book)

@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    service = BookService(db)
    return await service.delete_book(book_id)
