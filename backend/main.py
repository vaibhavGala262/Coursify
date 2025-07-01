from fastapi import FastAPI
import uvicorn 
import os 
from  dotenv import load_dotenv
from routers import users


load_dotenv()  # Load environment variables from .env file


app = FastAPI()
app.include_router(users.router)

PORT = int(os.getenv('PORT')) 


@app.get('/')
def main():
    return {'message': 'Hello, World!'}





if __name__ == '__main__':
    uvicorn.run('main:app' , host = 'localhost' , port =PORT  , reload = True ) 
