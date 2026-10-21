import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use the same port as your docker-compose.yml (left side of "XXXX:5432").
# Your Part 1 script uses 5433, so change the default below if that is your port.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://library:library@localhost:5433/library",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()