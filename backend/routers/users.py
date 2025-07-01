from fastapi import APIRouter
from utils.get_questions import get_mcq




router = APIRouter(prefix = '/users' , tags= ['users'])



@router.get('/')  #/users/
def get_users():
    return {'message': get_mcq("AI" , 3 , "Medium") }
