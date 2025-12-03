from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi import Depends, HTTPException, Request
from db.utils import conn_to_db
from models.model import User
from auth.security import verify_password, verify_jwt

def check_valid_user_from_db_and_get_user(
        user: HTTPBasicCredentials, 
        conn=Depends(conn_to_db)
        ) -> User:
    
    cursor = conn.cursor()
    cursor.execute('select username, roles, hash_psw, session_token from users where username = %s', (user.username,))
    raw_data = cursor.fetchone()
    if raw_data is None:
        raise HTTPException(status_code=401, detail='username invalid')
    _, db_roles, db_hash_psw, db_session = raw_data
    if not verify_password(user.password, db_hash_psw):
        raise HTTPException(status_code=401, detail='password invalid')
    
    return User(
        username=user.username, 
        hash_psw=db_hash_psw, 
        roles=db_roles, 
        session_token=db_session)

def base_auth(
        user: HTTPBasicCredentials = Depends(HTTPBasic()), 
        conn=Depends(conn_to_db)
        ) -> User:
    
    return check_valid_user_from_db_and_get_user(user=user, conn=conn)


def check_valid_session_token_and_get_user(req:Request) -> User:
    jwt_token = req.cookies.get('jwt_personal_session_token')
    if not jwt_token:
        raise HTTPException(status_code=401, detail='token invalid')
    try:
        payload = verify_jwt(token=jwt_token)
        return User(**payload)
    except:
        raise HTTPException(status_code=401, detail='token invalid')    
    
def require_roles(need_roles: list[str]):
    def dependency(user: User = Depends(check_valid_session_token_and_get_user)) -> User:
        fact_roles = set(user.roles or [])
        if not fact_roles.intersection(need_roles):
            raise HTTPException(status_code=403, detail='has not access')
        return user
    return dependency


# #проверить остаток запросов (это на потом)
# def asks_count(req:Request, con):

#     #1) get username from jwt in cookie
#     user = check_valid_session_token_and_get_user()
#     username = user.username

#     #2) get asks_cnt
#     cursor = con.cursor()
#     cursor.execute('select asks_cnt from users where username = %s', ( ,username))
#     data = cursor.fetchrow()[0]
#     return data