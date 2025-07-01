from models.theory import TheoryRequest, TheoryResponse
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import markdown
import re

load_dotenv()

model = os.getenv('MODEL')
api_key = os.getenv('GROQ_API_KEY')

if not model or not api_key:
    raise EnvironmentError("MODEL and GROQ_API_KEY must be set in the .env file")

# Load LLM
llm = ChatGroq(
    groq_api_key=api_key,
    model=model,
    temperature=0.2,
    max_tokens=3000
)

async def get_theory(request: TheoryRequest) -> TheoryResponse:
    """
    Generate theory content using ChatGroq
    """
    # Create prompt template
    system_prompt = """
You are an expert educational content generator.

Your task is to produce clean, structured, academic content without any reasoning, planning, or internal thoughts. 

DO NOT include any <think>, reflections, or explanations about how you are thinking or building the answer.  
ONLY return the final educational content in the exact format specified.

The output must strictly include:
1. ## Theory Content  
2. ## Key Concepts  
3. ## Examples  
4. ## Summary

Do not return anything outside these 4 sections. Do not include greetings, instructions, or commentary.
"""

    human_prompt = """
Topic: {topic}  
Subject: {subject}  
Level: {level}  
Learning Style: {learning_style}  
Max Length: {max_length} words  

Required Format:

## Theory Content  
[main theoretical explanation]

## Key Concepts  
- Concept 1: [short explanation]  
- Concept 2: [short explanation]  
- Concept 3: [short explanation]

## Examples  
- Example 1: [problem + step-by-step solution]  
- Example 2: [problem + step-by-step solution]

## Summary  
[final recap of the theory and applications]

Only return the above structure. Do not include any planning, internal thoughts, or explanation.
"""

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", human_prompt)
    ])

    # Create chain
    chain = prompt_template | llm | StrOutputParser()
    
    # Generate content
    content = await chain.ainvoke({
        "topic": request.topic,
        "subject": request.subject,
        "level": request.level,
        "learning_style": request.learning_style,
        "max_length": request.max_length
    })
    
    # Clean and format content
    content = clean_latex_and_format(content)
    
    # Extract key concepts and examples
    key_concepts, examples = _extract_concepts_and_examples(content)

    return TheoryResponse(
        topic=request.topic,
        content=content,
        key_concepts=key_concepts,
        examples=examples,
        level=request.level
    )

def _extract_concepts_and_examples(content: str):
    """Extract key concepts and examples from generated content"""
    lines = content.split('\n')
    key_concepts = []
    examples = []
    
    section = None
    
    for line in lines:
        line = line.strip()
        if line.lower().startswith("<h2>key concepts</h2>"):
            section = "concepts"
            continue
        elif line.lower().startswith("<h2>examples</h2>"):
            section = "examples"
            continue
        elif line.startswith("<h2>"):
            section = None
            continue

        if section == "concepts" and line.startswith("<li><strong>"):
            concept = re.sub(r"<[^>]+>", "", line).strip()
            key_concepts.append(concept)
        elif section == "examples" and line.startswith("<li><strong>"):
            example = re.sub(r"<[^>]+>", "", line).strip()
            examples.append(example)

    return key_concepts, examples

def clean_latex_and_format(content: str) -> str:
    """Clean LaTeX, remove think blocks, and format content"""
    # Remove <think> blocks and their content
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    # Fix escaped LaTeX and newlines
    content = content.replace("\\(", "(").replace("\\)", ")")
    content = re.sub(r"\\\\", r"\\", content)
    # Convert Markdown to HTML
    content = markdown.markdown(content)
    return content