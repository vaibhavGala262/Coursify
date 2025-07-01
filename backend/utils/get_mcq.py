from dotenv import load_dotenv
import os 
from langchain_groq import ChatGroq
from models.mcq_question import MCQOption, MCQuestion, MCQResponse
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser


load_dotenv() # Load environment variables from .env file

model = os.getenv('MODEL')
api_key = os.getenv('GROQ_API_KEY')

if not model or not api_key:
    raise EnvironmentError("MODEL and GROQ_API_KEY must be set in the .env file")

def get_mcq(topic: str, num_questions: int = 5, difficulty: str = "Medium"):
    # Initialize Groq LLM
    llm = ChatGroq(
        temperature=0.3,
        groq_api_key=api_key,
        model_name=model # or "llama2-70b-4096"
    )
    
    # Create output parser
    parser = PydanticOutputParser(pydantic_object=MCQResponse)
    
    # Define prompt template
    prompt = PromptTemplate(
        template="""
        Create {num_questions} multiple choice questions about {topic}.
        
        Requirements:
        - Difficulty level: {difficulty}
        - Each question should have exactly 4 options
        - Only one correct answer per question
        - Include detailed explanations
        - Cover different aspects of the topic
        - Make questions practical and application-based
        
        {format_instructions}
        
        Topic: {topic}
        Number of questions: {num_questions}
        Difficulty: {difficulty}
        """,
        input_variables=["topic", "num_questions", "difficulty"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Create chain
    chain = prompt | llm | parser
    
    # Execute
    try:
        result = chain.invoke({
            "topic": topic,
            "num_questions": num_questions,
            "difficulty": difficulty
        })
        return result
    except Exception as e:
        print(f"Error generating MCQs: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    topic = "AI"
    num_questions = 5
    difficulty = "Medium"
    
    mcq_response = get_mcq(topic, num_questions, difficulty)
    
    if mcq_response:
        for question in mcq_response.questions:
            print(f"Question: {question.question}")
            for option in question.options:
                print(f" - {option.option} (Correct: {option.is_correct})")
            print(f"Explanation: {question.explanation}\n")
    else:
        print("Failed to generate questions.")