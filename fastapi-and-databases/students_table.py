from database_connection import engine
from sqlalchemy import MetaData, Table, Column, Integer, String, CheckConstraint

metadata = MetaData()

students = Table(
    "students",
    metadata,
    Column("id", Integer, primary_key = True),
    Column("name", String, nullable = False),
    Column("age", Integer),
    CheckConstraint("age > 18", name = "age_check"),
    Column("city", String, nullable = True)
)

def create_tables():
    metadata.create_all(engine)