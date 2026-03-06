from fastapi import FastAPI, HTTPException, Query
from typing import Optional
app = FastAPI()

@app.get("/search")
def getData(name: Optional[str] = Query(default=None, description="Name of the person to search"), age: Optional[int] = Query(default=None, description="Age of the person to search")):
    if name == "Deepak" or age == 30:
        return {"name": name, "age": age}
    else:
        raise HTTPException(status_code=404, detail="Data not found")