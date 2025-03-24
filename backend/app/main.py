from fastapi import FastAPI, Request, Response
from app.utils.logger import log_event

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    log_event(f"Request: {request.method} {request.url}")
    return response

@app.post("/auth/login")
async def login(data: LoginData):
    # ... login logic ...
    if login_success:
        log_event(f"User {data.email} logged in successfully.")
    else:
        log_event(f"Failed login attempt for user {data.email}.", level="WARNING")
    return response

@app.post("/graphql")
async def handle_graphql(request: Request):
    # ... handle GraphQL request ...
    if subscription_error:
        log_event(f"Subscription error: {str(subscription_error)}", level="ERROR")
    return response

@app.middleware("http")
async def log_db_queries(request: Request, call_next):
    response = await call_next(request)
    log_event(f"Database query: {request.url}")
    return response

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}