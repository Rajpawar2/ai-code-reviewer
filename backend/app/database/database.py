from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.database.models import Base
from app.core.logging import logger

db_url = settings.normalized_database_url
connect_args = {}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Helper to format host for logging without exposing credentials
def _get_masked_db_host(raw_url: str) -> str:
    try:
        # Replace driver prefix for standard urlparse
        clean_url = raw_url.replace("postgresql+psycopg://", "http://").replace("postgres://", "http://").replace("postgresql://", "http://")
        parsed = urlparse(clean_url)
        return f"{parsed.hostname}:{parsed.port or 5432}/{parsed.path.lstrip('/')}"
    except Exception:
        return "configured database"

engine = create_engine(
    db_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    masked_target = _get_masked_db_host(db_url)
    
    # Check for misconfigured localhost in production
    is_localhost = "127.0.0.1" in db_url or "localhost" in db_url
    if settings.ENVIRONMENT.lower() == "production" and is_localhost:
        logger.error(
            "CRITICAL: Application is running in PRODUCTION mode, but DATABASE_URL is pointing to localhost (127.0.0.1)! "
            "Please configure the DATABASE_URL environment variable in the Render Dashboard with your Render PostgreSQL Internal/External connection string."
        )
    
    logger.info(f"Connecting to database at {masked_target}...")
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized and tables verified at {masked_target}.")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL at {masked_target}: {e}")
        if is_localhost:
            logger.error("Action Required: Set 'DATABASE_URL' in Render Web Service -> Environment to your Render PostgreSQL connection URL.")
        raise e


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
