import os

# Tests use SQLite, never your Postgres data. Must be set BEFORE importing app.*
os.environ["DATABASE_URL"] = "sqlite:///./test_bibliotech.db"

import pytest
from soap.database import Base, engine
from soap import models  # noqa: F401


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield