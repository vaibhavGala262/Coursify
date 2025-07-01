from fastapi import APIRouter
from utils.get_theory import get_theory
from models.theory import TheoryRequest



router = APIRouter(prefix = '/theory' , tags= ['theory'])


request = TheoryRequest(
    topic="Parabola",
    subject="Math",
    level="Advanced",
    learning_style="Visual",
    max_length=300
)


@router.get('/')
async def get_theory_ok():
    
    response = await get_theory(request)
    return {"message":response}