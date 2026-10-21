from sqlalchemy import Column, Integer, String, Float, CheckConstraint
from soap.database import Base


class Book(Base):
    __tablename__ = "soa_books"

    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    available_copies = Column(Integer, nullable=False)
    rental_price = Column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint("id > 0", name="ck_soa_id_positive"),
        CheckConstraint("available_copies >= 0", name="ck_soa_copies_positive"),
        CheckConstraint("rental_price >= 0", name="ck_soa_price_positive"),
    )