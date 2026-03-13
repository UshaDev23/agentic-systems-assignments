from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Custom Exception
@app.exception_handler(404)
async def not_found_exception(request: Request, exc):
    return JSONResponse(
        status_code = 404,
        content = {"message": "The requested resource was not found"}
    )


@app.get("/hello")
def get_message():
    return {"message":"Hello, Welcome to FastAPI!"}

@app.middleware("http")
async def middleware_func(request: Request, call_next):
    print("Before processing the request...")
    print(f"Request Method: {request.method}")
    print(f"Request Path: {request.url.path}")
    response = await call_next(request)
    print("After processing the request...")
    return response
