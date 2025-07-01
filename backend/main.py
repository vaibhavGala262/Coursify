from fastapi import FastAPI
import uvicorn 
import os 
from  dotenv import load_dotenv
from routers import questions , theory , ref



load_dotenv()  # Load environment variables from .env file


app = FastAPI()
app.include_router(questions.router)
app.include_router(theory.router)
app.include_router(ref.router)



PORT = int(os.getenv('PORT')) 


@app.get('/')
def main():
    return {'message': 'Hello, World!'}





if __name__ == '__main__':
    uvicorn.run('main:app' , host = 'localhost' , port =PORT  , reload = True ) 
