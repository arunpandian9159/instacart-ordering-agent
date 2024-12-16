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
from pydantic import BaseModel
# Load environment variables
load_dotenv()

class Selector(BaseModel):
    value: str



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
        
        return clean_html_file(html_content)

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

class PressKeyTool(BaseTool):
    name: str = "press_key"
    description: str = "Simulates pressing a keyboard key on the currently focused element"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, key: str, selector: str = None) -> str:
        """Presses a keyboard key. If selector is provided, focuses that element first"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            if selector:
                self.browser_tool.page.focus(selector)
            self.browser_tool.page.keyboard.press(key)
            return f"Successfully pressed {key} key"
        except Exception as e:
            return f"Error pressing key: {str(e)}"

class WaitTool(BaseTool):
    name: str = "wait"
    description: str = "Waits for a specified duration in milliseconds"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, duration_ms: int = 2000) -> str:
        """Waits for the specified duration in milliseconds"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            self.browser_tool.page.wait_for_timeout(duration_ms)
            return f"Successfully waited for {duration_ms}ms"
        except Exception as e:
            return f"Error while waiting: {str(e)}"

# Initialize tools
browser_tool = OpenBrowserTool()
navigate_tool = NavigateTool(browser_tool)
get_html_tool = GetHtmlTool(browser_tool)
save_html_tool = SaveHtmlTool(browser_tool)
fill_input_tool = FillInputTool(browser_tool)
click_element_tool = ClickElementTool(browser_tool)
screenshot_tool = ScreenshotTool(browser_tool)
press_key_tool = PressKeyTool(browser_tool)
wait_tool = WaitTool(browser_tool)



find_selector_agent = Agent(
    role='HTML and CSS Navigation Selection',
    goal="""
        Get the current page HTML using the tool and provide the most appropriate CSS selector to accomplish the task
        
        Return your response in this exact JSON format like this example:
        {{
            "selector": "the-css-selector",
            "action":  "search input"
        }}
        
        Prioritize selectors in this order:
        1. Unique IDs
        2. Aria labels or roles
        3. Data attributes
        4. Unique class combinations
        5. Element type + unique attributes""",
    backstory="""
    You are an expert at finding the best CSS selector for a given HTML element.
        """,
    tools=[get_html_tool],
    verbose=False,
    allow_delegation=False,
    output_json=Selector,
    llm=llm,
    memory=True
)


# Create a web automation agent
web_agent = Agent(
    role='Web Navigator',
    goal='Navigate and interact with web pages and output what action you took',
    backstory="""You are a web automation expert capable of browsing websites 
    and gathering information. You can open browsers, navigate to different URLs,
    fill in forms, click elements, press keyboard keys, and capture screenshots.""",
    tools=[browser_tool, navigate_tool, get_html_tool, save_html_tool, 
           fill_input_tool, click_element_tool, screenshot_tool, press_key_tool, wait_tool],
    llm=llm,
    memory=True
)

manager = Agent(
    role="Instacart Agent Manager",
    goal="Efficiently manage the crew and ensure the web agent navigates to the page and talks to the selector agent to find the best selector to interact with the search box on the website",
    backstory="You are an expert at managing agents and ensuring they work together to achieve a goal",
    allow_delegation=True,
    llm=llm,    
    memory=True
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
    description="Go to Instacart's website",
    expected_output="""Save the HTML to instacart.html and append the filepath to context. 
    Return a JSON object with status and filepath""",
    agent=web_agent,
    task_callbacks=on_task_start
)

find_selector_for_search_box = Task(
    description="""Read the HTML file from the shared state and find the best selector 
    for the search box. Store the selector in shared state.""",
    expected_output="Return a JSON object with the found selector",
    agent=find_selector_agent,
    task_callbacks=on_task_start
)

fill_search_box = Task(
    description="""Use the selector found by the selector agent to fill the input with apples on instacart and hit enter and wait for the page to load""",
    expected_output="We have ended up on the page with the results for apples",
    agent=web_agent,
    task_callbacks=on_task_start

)

capture_screenshot = Task(
    description="""Capture a screenshot of the page""",
    expected_output="The page should show the results for apples, capture a screenshot and save it to apples.png",
    agent=web_agent,
    task_callbacks=on_task_start
)

crew = Crew(
    agents=[web_agent, find_selector_agent],
    tasks=[navigate_to_instacart, find_selector_for_search_box, fill_search_box, capture_screenshot],
    manager_agent=manager,
    process=Process.sequential,
    planning=True,
    planning_llm=llm
)

result = crew.kickoff()

# Test the agent with the task
print("\n Crew's Response:")
print(result)
