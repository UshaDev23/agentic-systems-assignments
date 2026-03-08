from fastapi import FastAPI, HTTPException, Path, Query, Depends, Request
from crud_operations import insert_student, get_all_students, update_student_city, delete_student_with_age
from fastapi.responses import JSONResponse
from typing import Optional

app = FastAPI()


@app.post("/insert")
def add_student(name: str, age: int, city: Optional[str] = None):
        insert_student(name, age, city)
        return JSONResponse(
            status_code = 200,
            content = {"message":"Student Added Successfully"}
        )

@app.get("/get")
def get_students():
    students_data = get_all_students()
    return students_data

@app.patch("/update")
def update_city(city: str = Query(..., description = "The new city of Rahul")):
    update_student_city(city)
    return JSONResponse(
            status_code = 200,
            content = {"message":"City Updated Successfully"}
        )

@app.delete("/delete")
def delete_student(age: int = Query(..., description = "Age of the student to be deleted")):
    delete_student_with_age(age)
    return JSONResponse(
            status_code = 204,
            content = {"message":"Deleted student Successfully"}
        )

