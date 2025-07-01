from fastapi import APIRouter
from utils.get_mcq import get_mcq
from utils.get_theory_question import get_theory_questions



router = APIRouter(prefix = '/questions' , tags= ['questions'])



@router.get('/multi_choice_question')  #/users/
def get_multi_choice_question():
    return {'message': get_mcq("AI" , 3 , "Medium") }


@router.get('/theory_question' )  #/users/
def get_theory_question():
    return {'message': get_theory_questions("Computer networks" , 3 , "hard") }



