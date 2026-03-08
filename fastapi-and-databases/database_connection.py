# To connect to database
from sqlalchemy import create_engine
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, echo=True)
