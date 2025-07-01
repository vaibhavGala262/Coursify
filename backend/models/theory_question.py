from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional

class TheoryQuestion(BaseModel):
    question: str = Field(description="The theoretical question")
    question_type: str = Field(description="Type: Definition, Explanation, Comparison, Analysis, Application, Evaluation")
    difficulty: str = Field(description="Easy, Medium, Hard, Expert")
    topic_tags: List[str] = Field(description="Relevant topic tags")
    bloom_level: str = Field(description="Bloom's taxonomy level")
    estimated_time: int = Field(description="Estimated time to answer in minutes")
    key_concepts: List[str] = Field(description="Key concepts student should address")
    sample_answer_outline: List[str] = Field(description="Main points for a good answer")
    evaluation_criteria: List[str] = Field(description="What to look for when grading")
    prerequisite_knowledge: List[str] = Field(description="Required background knowledge")
    marks_allocation: int = Field(description="Suggested marks for this question")

class TheoryQuestionsResponse(BaseModel):
    questions: List[TheoryQuestion] = Field(description="List of generated theory questions")
    total_marks: int = Field(description="Total marks for all questions")
    exam_duration: int = Field(description="Suggested exam duration in minutes")