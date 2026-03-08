from database_connection import engine
from students_table import students
from sqlalchemy import insert, update, delete, select
from typing import Optional

# Create Student
def insert_student(name: str, age: int, city:Optional[str] = None):
    with engine.connect() as conn:
        query = insert(students).values(name=name, age=age, city=city)
        conn.execute(query)
        conn.commit()

def delete_all():
    with engine.connect() as conn:
        query = delete(students)
        conn.execute(query)
        conn.commit()

def get_all_students():
    with engine.connect() as conn:
        query = select(students)
        result = conn.execute(query)
        return [dict(row._mapping) for row in result]

def update_student_city(city: str):
    with engine.connect() as conn:
        query = update(students).where(students.c.name == "Rahul").values(city = city)
        conn.execute(query)
        conn.commit()

def delete_student_with_age(age: int):
    with engine.connect() as conn:
        query = delete(students).where(students.c.age < age)
        conn.execute(query)
        conn.commit()