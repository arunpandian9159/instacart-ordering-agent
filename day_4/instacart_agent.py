from crewai import Agent, Task, LLM, Crew, Process
from crewai.tools import BaseTool
from litellm import completion
import json
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from typing import Optional, Any
from pydantic import Field
from bs4 import BeautifulSoup
from html_utils import clean_html_file  # Import the function
from selector_finder_agent import find_selector_agent
# Load environment variables
load_dotenv()

# Load Vertex AI credentials
with open(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'), 'r') as file:
    vertex_credentials = json.load(file)
vertex_credentials_json = json.dumps(vertex_credentials)

llm = LLM(
    model="gemini-1.5-flash-002",
    custom_llm_provider="vertex_ai",
    api_key=vertex_credentials_json
)
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

class GetHtmlTool(BaseTool):
    name: str = "get_html"
    description: str = "Gets the HTML from the current page and cleans it using clean_html_file"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, file_path: str, context: list = None) -> str:
        """Gets the HTML from the current page and cleans it"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        html_content = self.browser_tool.page.content()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        clean_html_file(file_path)
        
        if context is not None:
            context.append({
                "html_file_path": file_path
            })
        
        return json.dumps({
            "status": "success",
            "file_path": file_path
        })

class SaveHtmlTool(BaseTool):
    name: str = "save_html"
    description: str = "Saves the HTML content to a specified file path"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, file_path: str) -> str:
        """Saves the HTML content to a specified file path"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        # Get the HTML content from the page
        html_content = self.browser_tool.page.content()
        
        # Write the HTML content to a file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(clean_html_file(html_content))
        
        return f"HTML content saved to {file_path}"

class FillInputTool(BaseTool):
    name: str = "fill_input"
    description: str = "Fills an input element identified by a selector with specified text"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, selector: str, text: str) -> str:
        """Fills an input element with text"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            self.browser_tool.page.fill(selector, text)
            return f"Successfully filled input {selector} with text: {text}"
        except Exception as e:
            return f"Error filling input: {str(e)}"

class ClickElementTool(BaseTool):
    name: str = "click_element"
    description: str = "Clicks an element identified by a selector"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, selector: str) -> str:
        """Clicks an element"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            self.browser_tool.page.click(selector)
            return f"Successfully clicked element: {selector}"
        except Exception as e:
            return f"Error clicking element: {str(e)}"

class ScreenshotTool(BaseTool):
    name: str = "take_screenshot"
    description: str = "Takes a screenshot of the current page or a specific element"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, file_path: str, selector: str = None) -> str:
        """Takes a screenshot and saves it to the specified path.
        If selector is provided, screenshots only that element."""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            if selector:
                # Find the element and screenshot just that element
                element = self.browser_tool.page.locator(selector)
                element.screenshot(path=file_path)
                return f"Successfully captured screenshot of element {selector} to {file_path}"
            else:
                # Screenshot the entire page
                self.browser_tool.page.screenshot(path=file_path)
                return f"Successfully captured full page screenshot to {file_path}"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"

# Initialize tools
browser_tool = OpenBrowserTool()
navigate_tool = NavigateTool(browser_tool)
get_html_tool = GetHtmlTool(browser_tool)
save_html_tool = SaveHtmlTool(browser_tool)
fill_input_tool = FillInputTool(browser_tool)
click_element_tool = ClickElementTool(browser_tool)
screenshot_tool = ScreenshotTool(browser_tool)

# Create a web automation agent
web_agent = Agent(
    role='Web Navigator',
    goal='Navigate and interact with web pages',
    backstory="""You are a web automation expert capable of browsing websites 
    and gathering information. You can open browsers, navigate to different URLs,
    fill in forms, click elements, and capture screenshots.""",
    tools=[browser_tool, navigate_tool, get_html_tool, save_html_tool, 
           fill_input_tool, click_element_tool, screenshot_tool],
    llm=llm
)

manager = Agent(
    role="Instacart Agent Manager",
    goal="Efficiently manage the crew and ensure the web agent navigates to the page and talks to the selector agent to find the best selector to interact with the search box on the website",
    backstory="You are an expert at managing agents and ensuring they work together to achieve a goal",
    allow_delegation=True,
)

# Add these callback functions after the imports
def on_task_start(task):
    print(f"\n➡️ Starting task: {task.description}")

def on_task_end(task, output):
    print(f"\n✅ Finished task: {task.description}")
    print(f"📝 Output: {output}")

# Initialize shared context
shared_context = []

# Modify the tasks to use the list context
navigate_to_instacart = Task(
    description="Go to Instacart and save the HTML to a file called instacart.html",
    expected_output="""Save the HTML to instacart.html and append the filepath to context. 
    Return a JSON object with status and filepath""",
    agent=web_agent,
    context=shared_context,
    task_callbacks={
        "on_start": on_task_start,
        "on_end": on_task_end
    }
)

find_selector_for_instacart = Task(
    description="""Read the HTML file from the shared state and find the best selector 
    for the search box. Store the selector in shared state.""",
    expected_output="Return a JSON object with the found selector",
    agent=find_selector_agent,
    context=shared_context,
    task_callbacks={
        "on_start": on_task_start,
        "on_end": on_task_end
    }
)

search_for_apples = Task(
    description="""Use the selector from shared state to search for apples on instacart and save a screenshot at apples.png""",
    expected_output="Save results to apples.html and return success status",
    agent=web_agent,
    context=shared_context,
    task_callbacks={
        "on_start": on_task_start,
        "on_end": on_task_end
    }
)

crew = Crew(
    agents=[web_agent, find_selector_agent],
    tasks=[navigate_to_instacart, find_selector_for_instacart, search_for_apples],
    manager_agent=manager,
    process=Process.sequential,
)

result = crew.kickoff()

# Test the agent with the task
print("\n Crew's Response:")
print(result)
