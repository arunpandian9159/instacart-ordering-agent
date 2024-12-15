from pydantic import BaseModel
from crewai import Agent, Task, LLM
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    SerperDevTool,
    WebsiteSearchTool,
    BaseTool
)
from litellm import completion
import json
import os
from dotenv import load_dotenv
from typing import Optional

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

# Initialize shared context
shared_context = []

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

class SelectorFinderTool(BaseTool):
    name: str = "selector_finder"
    description: str = "Finds the best selector for a given HTML element"
    
    def _run(self, context: list = None) -> str:
        if not context:
            return json.dumps({
                "status": "error",
                "message": "No context provided"
            })
            
        # Find the most recent file path from context
        file_path = None
        for item in reversed(context):
            if "html_file_path" in item:
                file_path = item["html_file_path"]
                break
                
        if not file_path:
            return json.dumps({
                "status": "error",
                "message": "No HTML file path in context"
            })
            
        # Find selector logic here...
        selector = "your_found_selector"
        
        # Add the selector to context
        context.append({
            "search_selector": selector
        })
        
        return json.dumps({
            "status": "success",
            "selector": selector
        })


