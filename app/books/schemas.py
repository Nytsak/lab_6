from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from enum import Enum
from typing import Optional, List

class BookStatus(str, Enum):
    AVAILABLE = "available"
    ISSUED = "issued"

class BookRequest(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: BookStatus = BookStatus.AVAILABLE
    release_year: int = Field(..., gt=0)

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class BookResponse(BaseModel):
    id: UUID
    title: str
    author: str
    description: Optional[str]
    status: BookStatus
    release_year: int

    model_config = ConfigDict(from_attributes=True)

class PaginatedBooksResponse(BaseModel):
    total: int
    limit: int
    offset: int
    next_page: Optional[str] = None
    prev_page: Optional[str] = None
    items: List[BookResponse]
