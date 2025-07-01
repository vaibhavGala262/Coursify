from langchain_groq import ChatGroq
from langchain.output_parsers import PydanticOutputParser

from models.theory_question import TheoryQuestion , TheoryQuestionsResponse
import os 
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
import json
from typing import List, Optional, Dict, Any
import re


load_dotenv() # Load environment variables from .env file




model = os.getenv('MODEL')
api_key = os.getenv('GROQ_API_KEY')

if not model or not api_key:
    raise EnvironmentError("MODEL and GROQ_API_KEY must be set in the .env file")



def extract_json_from_response(text: str) -> Optional[Dict[Any, Any]]:
    """Extract JSON from LLM response with multiple fallback methods"""
    
    # Method 1: Remove thinking tags and extract JSON
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Method 2: Remove code blocks
    if '```' in cleaned_text:
        # Extract content between code blocks
        code_block_pattern = r'```(?:json)?\s*(.*?)\s*```'
        matches = re.findall(code_block_pattern, cleaned_text, re.DOTALL)
        if matches:
            cleaned_text = matches[0]
    
    # Method 3: Find JSON-like structure
    json_patterns = [
        r'\{.*\}',  # Basic JSON pattern
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested JSON pattern
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, cleaned_text, re.DOTALL)
        for match in matches:
            try:
                # Clean the match
                match = match.strip()
                parsed = json.loads(match)
                if isinstance(parsed, dict) and 'questions' in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue
    
    # Method 4: Try to find JSON starting with specific structure
    start_patterns = [
        r'(\{"questions":\s*\[.*?\]\s*,.*?\})',
        r'(\{[^}]*"questions"[^}]*\})',
    ]
    
    for pattern in start_patterns:
        matches = re.findall(pattern, cleaned_text, re.DOTALL)
        for match in matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, dict) and 'questions' in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue
    
    return None


def create_fallback_response(topic: str, num_questions: int = 3) -> TheoryQuestionsResponse:
    """Create a fallback response when LLM fails"""
    
    fallback_questions = []
    question_types = ["Definition", "Explanation", "Analysis"]
    marks = [10, 15, 20]
    
    for i in range(min(num_questions, 3)):
        question = TheoryQuestion(
            question=f"Define and explain the key concepts of {topic}. Discuss their practical applications.",
            question_type=question_types[i],
            difficulty="Medium",
            topic_tags=[topic, "Theory"],
            bloom_level="Understand",
            estimated_time=15,
            key_concepts=[f"{topic} fundamentals", "Applications", "Key principles"],
            sample_answer_outline=[
                f"Define {topic}",
                "Explain core concepts",
                "Discuss applications",
                "Provide examples"
            ],
            evaluation_criteria=[
                "Accuracy of definition",
                "Clarity of explanation",
                "Relevant examples",
                "Logical structure"
            ],
            prerequisite_knowledge=[f"Basic understanding of {topic}"],
            marks_allocation=marks[i]
        )
        fallback_questions.append(question)
    
    return TheoryQuestionsResponse(
        questions=fallback_questions,
        total_marks=sum(marks[:num_questions]),
        exam_duration=num_questions * 15
    )


def get_theory_questions_robust(topic: str, 
                              num_questions: int = 3, 
                              difficulty: str = "Medium",
                              use_fallback: bool = True) -> Optional[TheoryQuestionsResponse]:
    """
    Robust theory questions generator with multiple retry strategies
    """
    
    try:
        llm = ChatGroq(
            temperature=0.1,
            groq_api_key=api_key,  # Replace with your actual key
            model=model,
            max_tokens=4000
        )
    except Exception as e:
        print(f"Failed to initialize LLM: {e}")
        if use_fallback:
            return create_fallback_response(topic, num_questions)
        return None
    
    # Ultra-simple prompt focusing only on JSON output
    prompt_template = """Create {num_questions} theory questions about {topic}.

Return ONLY this JSON format (no other text):

{{
  "questions": [
    {{
      "question": "Your question text here",
      "question_type": "Definition",
      "difficulty": "{difficulty}",
      "topic_tags": ["{topic}"],
      "bloom_level": "Understand",
      "estimated_time": 15,
      "key_concepts": ["concept1", "concept2"],
      "sample_answer_outline": ["point1", "point2", "point3"],
      "evaluation_criteria": ["criteria1", "criteria2"],
      "prerequisite_knowledge": ["prereq1"],
      "marks_allocation": 15
    }}
  ],
  "total_marks": 45,
  "exam_duration": 45
}}

Topic: {topic}
Questions: {num_questions}
Difficulty: {difficulty}"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["topic", "num_questions", "difficulty"]
    )
    
    # Try multiple approaches
    approaches = [
        {"model":model ,"temperature": 0.0},
        { "model":model ,"temperature": 0.1},
        {"model":model, "temperature": 0.0}
    ]
    
    for i, approach_params in enumerate(approaches):
        try:
            print(f"Trying approach {i+1}...")
            
            # Update LLM with new parameters
            current_llm = ChatGroq(
                groq_api_key=api_key,  # Replace with your actual key
                max_tokens=4000,
                **approach_params
            )
            
            # Generate response
            formatted_prompt = prompt.format(
                topic=topic,
                num_questions=num_questions,
                difficulty=difficulty
            )
            
            response = current_llm.invoke(formatted_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"Response length: {len(response_text)}")
            print(f"Response preview: {response_text[:200]}...")
            
            # Extract JSON
            extracted_json = extract_json_from_response(response_text)
            
            if extracted_json:
                print("Successfully extracted JSON")
                
                # Validate required fields
                if 'questions' not in extracted_json:
                    extracted_json['questions'] = []
                if 'total_marks' not in extracted_json:
                    extracted_json['total_marks'] = sum(q.get('marks_allocation', 15) for q in extracted_json['questions'])
                if 'exam_duration' not in extracted_json:
                    extracted_json['exam_duration'] = len(extracted_json['questions']) * 15
                
                # Try to create Pydantic model
                try:
                    result = TheoryQuestionsResponse(**extracted_json)
                    print(f"Successfully created {len(result.questions)} questions")
                    return result
                except Exception as validation_error:
                    print(f"Validation error: {validation_error}")
                    continue
            else:
                print("Could not extract valid JSON")
                
        except Exception as e:
            print(f"Approach {i+1} failed: {e}")
            continue
    
    print("All approaches failed")
    
    # Return fallback if enabled
    if use_fallback:
        print("Using fallback response")
        return create_fallback_response(topic, num_questions)
    
    return None


def get_theory_questions(topic : str , num_questions: int , difficulty: str):
    """Test function"""
    result = get_theory_questions_robust(
        topic=topic,
        num_questions=num_questions,
        difficulty=difficulty
    )
    
    if result:
        return result
    else:
        print("Failed to generate questions")


