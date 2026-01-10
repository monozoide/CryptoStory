import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()


def get_database_url(testing: bool = False):
    db_name = os.getenv("DB_NAME", "cryptostory") + ("_test" if testing else "")
    return f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{db_name}"


DATABASE_URL = get_database_url()
async_engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession)
