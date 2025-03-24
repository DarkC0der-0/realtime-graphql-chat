from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from app.utils.logger import log_event

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    log_event(f"Request: {request.method} {request.url}")
    return response
class LoginData(BaseModel):
    email: str
    password: str

@app.post("/auth/login")
async def login(data: LoginData):
    def authenticate_user(email: str, password: str) -> bool:
        return email == "test@example.com" and password == "securepassword"

    login_success = authenticate_user(data.email, data.password)
    if login_success:
        log_event(f"User {data.email} logged in successfully.")
        return {"message": "Login successful"}
    else:
        log_event(f"Failed login attempt for user {data.email}.", level="WARNING")
        return {"message": "Invalid credentials"}, 401

@app.post("/graphql")
async def handle_graphql(request: Request):
    subscription_error = None  
    if subscription_error:
        log_event(f"Subscription error: {str(subscription_error)}", level="ERROR")
        return {"error": "Subscription error occurred"}, 500
    return {"message": "GraphQL request handled successfully"}

@app.middleware("http")
async def log_db_queries(request: Request, call_next):
    response = await call_next(request)
    log_event(f"Database query: {request.url}")
    return response

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}