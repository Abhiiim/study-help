import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

# from router.url_router import url_router
# from db.base import create_tables
# from router.auth_router import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables...")
    # await asyncio.to_thread(create_tables)
    yield

app = FastAPI(lifespan=lifespan)

# app.add_middleware(
#     SessionMiddleware,
#     secret_key="SUPER_SECRET_KEY"
# )

@app.get("/")
def root():
    return {"message": "Hello World"}

# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(url_router, tags=["URL"])