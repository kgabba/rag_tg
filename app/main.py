from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from auth.routers import router_auth, router_bd
import psycopg2
from db.utils import DB_URL
from llm.routers import router_llm
import asyncio

@asynccontextmanager
async def lifespan(api: FastAPI):
    try:
        await asyncio.sleep(10) #ждем пока постгрес поднимется
        api.state.conn = psycopg2.connect(DB_URL)
        api.state.conn.autocommit = True
        print('подключение БД успешно создано')
    except Exception as e:
        print('ошибка подключения к БД:', e)
        raise RuntimeError('Ошибка подключения к БД')
    
    yield
    
    api.state.conn.close()
    print('Подключение к БД остановлено')


api = FastAPI(lifespan=lifespan)

api.include_router(router_auth)
api.include_router(router_bd)
api.include_router(router_llm)

if __name__ == '__main__':
    uvicorn.run(
        "main:api",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

