from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from typing import Optional, List
import os

# Pydantic models
class TheoryRequest(BaseModel):
    topic: str
    subject: str
    level: Optional[str] = "beginner"
    learning_style: Optional[str] = "visual"
    max_length: Optional[int] = 1000

class TheoryResponse(BaseModel):
    topic: str
    content: str
    key_concepts: List[str]
    examples: List[str]
    level: str
