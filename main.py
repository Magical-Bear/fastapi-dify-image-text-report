# import asyncio
# import sys
#
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
import uvicorn
import os
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from endpoints.v1 import repair_qa
from middlewares.init_lifespan import tai_middleware

app = FastAPI(lifespan=tai_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repair_qa, prefix="/api/qa")



if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=int((os.getenv("PORT"))))
