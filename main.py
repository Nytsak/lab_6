from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.books.router import router as book_router
from app.auth.router import router as auth_router
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.books.models
    import app.auth.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Library API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(book_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
