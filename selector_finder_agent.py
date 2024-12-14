from pydantic import BaseModel
from crewai import Agent, Task, LLM
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool
)
from litellm import completion
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Load Vertex AI credentials
with open(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), 'r') as file:
    vertex_credentials = json.load(file)
vertex_credentials_json = json.dumps(vertex_credentials)

llm = LLM(
    model="gemini-2.0-flash-exp",
    custom_llm_provider="vertex_ai",
    api_key=vertex_credentials_json
)

# Define the Pydantic model for the blog
class Selector(BaseModel):
    value: str

file_tool = FileReadTool()

find_selector_agent = Agent(
    role='HTML and CSS Navigation Selection',
    goal='Identify the most reliable CSS selector for a given objective',
    backstory="""Analyze the following HTML and provide the most appropriate CSS selector
        
        Return your response in this exact JSON format:
        {{
            "selector": "the-css-selector",
        }}
        
        Prioritize selectors in this order:
        1. Unique IDs
        2. Aria labels or roles
        3. Data attributes
        4. Unique class combinations
        5. Element type + unique attributes
        """,
    verbose=False,
    allow_delegation=False,
    output_json=Selector,
    llm=llm,
    tools=[file_tool]

)


find_serach_box = Task(
    description="Read a html file called index.html and find the best selector to interact with the search box on the website",
    expected_output="Return a structured JSON object with the CSS selector",
    agent=find_selector_agent,
)

selector_result = find_selector_agent.execute_task(find_serach_box)
print(selector_result)