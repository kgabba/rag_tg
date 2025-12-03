import os
from fastapi import Request 

DB_URL = os.getenv('DB_URL')

def conn_to_db(req:Request):
    return req.app.state.conn