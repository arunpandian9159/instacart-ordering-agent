from crewai import Agent, Task
from crewai.tools import BaseTool
from litellm import completion
import json
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from typing import Optional, Any
from pydantic import Field

# Load environment variables
load_dotenv()

# Load Vertex AI credentials
with open(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), 'r') as file:
    vertex_credentials = json.load(file)
vertex_credentials_json = json.dumps(vertex_credentials)

# Custom LLM class to use LiteLLM with CrewAI
class LiteLLMWrapper:
    def __init__(self, vertex_credentials):
        self.vertex_credentials = vertex_credentials
    
    def __call__(self, prompt):
        response = completion(
            model="gemini-2.0-flash-002",
            messages=[{"content": prompt, "role": "user"}],
            vertex_credentials=self.vertex_credentials
        )
        return response.choices[0].message.content

# Initialize the custom LLM
litellm_model = LiteLLMWrapper(vertex_credentials_json)

# Custom Playwright Tools
class OpenBrowserTool(BaseTool):
    name: str = "open_browser"
    description: str = "Opens a new browser instance. Specify browser_type as 'chromium', 'firefox', or 'webkit'"
    playwright: Optional[Any] = Field(default=None)
    browser: Optional[Any] = Field(default=None)
    page: Optional[Any] = Field(default=None)
    
    def __init__(self):
        super().__init__()
    
    def _run(self, browser_type: str = 'chromium') -> str:
        """Opens a new browser instance"""
        self.playwright = sync_playwright().start()
        if browser_type == 'chromium':
            self.browser = self.playwright.chromium.launch(headless=False)
        elif browser_type == 'firefox':
            self.browser = self.playwright.firefox.launch(headless=False)
        elif browser_type == 'webkit':
            self.browser = self.playwright.webkit.launch(headless=False)
        self.page = self.browser.new_page()
        return "Browser opened successfully"

class NavigateTool(BaseTool):
    name: str = "navigate"
    description: str = "Navigates to a specified URL in the opened browser"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, url: str) -> str:
        """Navigates to a specified URL"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        self.browser_tool.page.goto(url)
        return f"Navigated to {url} successfully"

# Initialize tools
browser_tool = OpenBrowserTool()
navigate_tool = NavigateTool(browser_tool)

# Create a web automation agent
web_agent = Agent(
    role='Web Navigator',
    goal='Navigate and interact with web pages',
    backstory="""You are a web automation expert capable of browsing websites 
    and gathering information. You can open browsers and navigate to different URLs.""",
    tools=[browser_tool, navigate_tool],
    llm="gemini-1.5-flash-002"
)

web_task = Task(
    description="Open a browser and navigate to 'https://www.instacart.com'",
    expected_output="Confirmation of successful browser opening and navigation",
    agent=web_agent
)

# Test the agent with the task
print("\nWeb Agent's Response:")
web_result = web_agent.execute_task(web_task)
print(web_result)

