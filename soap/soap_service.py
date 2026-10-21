from wsgiref.simple_server import make_server

from spyne import Application, ServiceBase, rpc, Integer, Unicode, Float, Fault
from spyne.model.complex import ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from sqlalchemy.exc import IntegrityError

from soap.database import SessionLocal
from soap.models import Book

NS = "bibliotech.soap"


class BookType(ComplexModel):
    __namespace__ = NS
    id = Integer
    title = Unicode
    author = Unicode
    available_copies = Integer
    rental_price = Float


def to_type(b: Book) -> BookType:
    return BookType(
        id=b.id,
        title=b.title,
        author=b.author,
        available_copies=b.available_copies,
        rental_price=b.rental_price,
    )


def validate(id, title, author, available_copies, rental_price):
    if id is None or id <= 0:
        raise Fault("Client.InvalidId", "The id must be a positive integer.")
    if not title or not title.strip():
        raise Fault("Client.InvalidTitle", "The title is required.")
    if not author or not author.strip():
        raise Fault("Client.InvalidAuthor", "The author is required.")
    if available_copies is None or available_copies < 0:
        raise Fault("Client.InvalidCopies", "available_copies must be >= 0.")
    if rental_price is None or rental_price < 0:
        raise Fault("Client.InvalidPrice", "rental_price must be >= 0.")


def check_id(id):
    if id is None or id <= 0:
        raise Fault("Client.InvalidId", "The id must be a positive integer.")


class BookService(ServiceBase):
    @rpc(Integer, Unicode, Unicode, Integer, Float, _returns=BookType)
    def CreateBook(ctx, id, title, author, available_copies, rental_price):
        validate(id, title, author, available_copies, rental_price)
        with SessionLocal() as s:
            if s.get(Book, id) is not None:
                raise Fault("Client.DuplicateId", f"Book {id} already exists.")
            book = Book(
                id=id,
                title=title.strip(),
                author=author.strip(),
                available_copies=available_copies,
                rental_price=rental_price,
            )
            s.add(book)
            try:
                s.commit()
            except IntegrityError:
                s.rollback()
                raise Fault("Client.Constraint", "Database constraint violated.")
            s.refresh(book)
            return to_type(book)

    @rpc(Integer, _returns=BookType)
    def GetBook(ctx, id):
        check_id(id)
        with SessionLocal() as s:
            book = s.get(Book, id)
            if book is None:
                raise Fault("Client.NotFound", f"Book {id} not found.")
            return to_type(book)

    @rpc(Integer, Unicode, Unicode, Integer, Float, _returns=BookType)
    def UpdateBook(ctx, id, title, author, available_copies, rental_price):
        validate(id, title, author, available_copies, rental_price)
        with SessionLocal() as s:
            book = s.get(Book, id)
            if book is None:
                raise Fault("Client.NotFound", f"Book {id} not found.")
            book.title = title.strip()
            book.author = author.strip()
            book.available_copies = available_copies
            book.rental_price = rental_price
            s.commit()
            s.refresh(book)
            return to_type(book)

    @rpc(Integer, _returns=Unicode)
    def DeleteBook(ctx, id):
        check_id(id)
        with SessionLocal() as s:
            book = s.get(Book, id)
            if book is None:
                raise Fault("Client.NotFound", f"Book {id} not found.")
            s.delete(book)
            s.commit()
            return f"Book {id} deleted."


application = Application(
    [BookService],
    tns=NS,
    name="BiblioTechService",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)
wsgi_app = WsgiApplication(application)

if __name__ == "__main__":
    print("SOAP service on http://localhost:8000/  (WSDL: http://localhost:8000/?wsdl)")
    make_server("0.0.0.0", 8000, wsgi_app).serve_forever()