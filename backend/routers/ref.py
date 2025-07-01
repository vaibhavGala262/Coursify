from fastapi import APIRouter
from utils.get_theory import get_theory
from models.theory import TheoryRequest
from utils.get_ytlinks import get_yt_links 
from utils.get_book_links import suggest_books



router = APIRouter(prefix = '/refs' , tags= ['refs'])



@router.get('/youtube')
def fn():
    return {'message': get_yt_links()}


@router.get('/books')
def fn():
    query = "Full Parabola Math"
    return {'message': suggest_books(query)}