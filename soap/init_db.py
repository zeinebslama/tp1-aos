from soap.database import engine, Base
from soap import models  # noqa: F401

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Table 'soa_books' created.")