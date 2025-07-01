
import os
from langchain_community.tools.google_books import GoogleBooksQueryRun
from langchain_community.utilities.google_books import GoogleBooksAPIWrapper
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv



load_dotenv() # Load environment variables from .env file




model = os.getenv('MODEL')
api_key = os.getenv('GROQ_API_KEY')
books_api_key = os.getenv('GOOGLE_BOOKS_API_KEY')

llm = ChatGroq(
    groq_api_key=api_key,
    model=model,
    temperature=0.2,
    max_tokens=300
)


tool = GoogleBooksQueryRun(api_wrapper=GoogleBooksAPIWrapper())

prompt = PromptTemplate.from_template(
    "Return the keyword,or appropriate context that the user is looking for from this text: {text}"
)


def suggest_books(query):
    chain = prompt | llm | StrOutputParser()
    keyword = chain.invoke({"text": query})
    return tool.run(keyword)





