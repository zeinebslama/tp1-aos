from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Path
from sqlalchemy.orm import Session

from soap.database import Base, SessionLocal, engine
from soap.models import Book
from soap.schemas import BookCreate, BookOut, BookUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="BiblioTech REST API",
    description="CRUD service for the BiblioTech book catalogue (Lab 1, Part 3).",
    version="1.0.0",
    lifespan=lifespan,
)


def get_db():
    with SessionLocal() as db:
        yield db


@app.get("/books", response_model=list[BookOut], summary="List all books")
def list_books(db: Session = Depends(get_db)):
    return db.query(Book).order_by(Book.id).all()


@app.get("/books/{book_id}", response_model=BookOut, summary="Get one book")
def get_book(book_id: int = Path(gt=0), db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(404, f"Book {book_id} not found")
    return book


@app.post("/books", response_model=BookOut, status_code=201, summary="Create a book")
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    if db.get(Book, data.id) is not None:
        raise HTTPException(409, f"Book {data.id} already exists")
    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@app.put("/books/{book_id}", response_model=BookOut, summary="Update a book")
def update_book(data: BookUpdate, book_id: int = Path(gt=0), db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(404, f"Book {book_id} not found")
    for field, value in data.model_dump().items():
        setattr(book, field, value)
    db.commit()
    db.refresh(book)
    return book


@app.delete("/books/{book_id}", status_code=204, summary="Delete a book")
def delete_book(book_id: int = Path(gt=0), db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(404, f"Book {book_id} not found")
    db.delete(book)
    db.commit()