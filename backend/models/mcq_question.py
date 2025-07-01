from pydantic import BaseModel , Field 
from typing import List

class MCQOption(BaseModel):
    option: str = Field(description="The option text")
    is_correct: bool = Field(description="Whether this option is correct")

class MCQuestion(BaseModel):
    question: str = Field(description="The multiple choice question")
    options: List[MCQOption] = Field(description="List of 4 options")
    explanation: str = Field(description="Explanation of the correct answer")
    difficulty: str = Field(description="Easy, Medium, or Hard")
    topic_tags: List[str] = Field(description="Relevant topic tags")

class MCQResponse(BaseModel):
    questions: List[MCQuestion] = Field(description="List of generated MCQs")



    