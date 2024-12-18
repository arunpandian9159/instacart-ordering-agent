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
from pydantic import BaseModel
# Load environment variables
load_dotenv()

class Selector(BaseModel):
    value: str
    action: str



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

class ClickButtonWithTextTool(BaseTool):
    name: str = "click_button_with_text"
    description: str = "Finds and clicks a button or element by its text content"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self, text: str) -> str:
        """Finds an element by text and clicks it"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            # Find the element by text
            element = self.browser_tool.page.get_by_text(text)
            
            # Wait for element to be visible
            element.wait_for(state='visible')
            
            # Get element's bounding box for debugging
            box = element.bounding_box()
            if not box:
                return f"Element with text '{text}' not found or not visible"
            
            print(f"Found button at coordinates: x={box['x']}, y={box['y']}")
            
            # Click the element
            element.click()
            
            return f"Successfully clicked element with text: {text} at coordinates x={box['x']}, y={box['y']}"
        except Exception as e:
            return f"Error finding or clicking element: {str(e)}"

class GetHumanInputTool(BaseTool):
    name: str = "get_human_input"
    description: str = "Gets input from the human user"
    
    def _run(self, prompt: str = "Please enter your input") -> str:
        """Gets input from the human user with a custom prompt"""
        try:
            user_input = input(f"\n👤 {prompt}: ")
            return user_input.strip()
        except Exception as e:
            return f"Error getting human input: {str(e)}"

# Add this new tool after other tool definitions

class ClickContinueAfterPhoneTool(BaseTool):
    name: str = "click_continue_after_phone"
    description: str = "Specifically finds and clicks the Continue button that appears after entering phone number"
    browser_tool: OpenBrowserTool = Field(default=None)
    
    def __init__(self, browser_tool: OpenBrowserTool):
        super().__init__(browser_tool=browser_tool)
    
    def _run(self) -> str:
        """Finds and clicks the Continue button after phone number entry"""
        if not self.browser_tool.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            # Use a more specific selector that targets the continue button after phone input
            # This button typically appears in a form or container after the phone input
            button = self.browser_tool.page.locator('button:has-text("Continue"):right-of([placeholder="Phone number"])')
            
            # Wait for element to be visible and clickable
            button.wait_for(state='visible')
            
            # Get element's bounding box for debugging
            box = button.bounding_box()
            if not box:
                return "Continue button not found or not visible"
            
            print(f"Found Continue button at coordinates: x={box['x']}, y={box['y']}")
            
            # Click the button
            button.click()
            
            return f"Successfully clicked Continue button at coordinates x={box['x']}, y={box['y']}"
        except Exception as e:
            return f"Error finding or clicking Continue button: {str(e)}"

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
click_button_with_text_tool = ClickButtonWithTextTool(browser_tool)
human_input_tool = GetHumanInputTool()
click_continue_after_phone_tool = ClickContinueAfterPhoneTool(browser_tool)



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
    find elements by their text, move the mouse naturally, and interact with pages.""",
    tools=[
        browser_tool, 
        navigate_tool, 
        get_html_tool, 
        save_html_tool, 
        fill_input_tool, 
        click_element_tool, 
        click_button_with_text_tool, 
        screenshot_tool, 
        press_key_tool, 
        wait_tool,
        human_input_tool,
        click_continue_after_phone_tool  # Add the new tool
    ],
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
    description="Go to Instacart's Login https://instacart.com/login website",
    expected_output="""The browser should be opened and navigated to the Instacart website""",
    agent=web_agent,
    task_callbacks=on_task_start
)

find_and_click_continue_with_phone = Task(
    description="""
    Find and click the "Continue with phone" button:

    1. Wait briefly for the page to load fully
    2. Use click_button_with_text_tool to locate and click the button with text "Continue with phone"
    3. Wait briefly to ensure the phone input field becomes visible
    
    Use these tools in sequence:
    1. wait_tool - Wait 5 seconds for page to load fully
    2. click_button_with_text_tool - To find and click the "Continue with phone" button
    3. wait_tool - Wait 2 seconds for phone input to appear
    """,
    expected_output="""Successfully clicked the Continue with phone button and arrived at the phone input screen""",
    agent=web_agent,
    task_callbacks=on_task_start
)

fill_phone_number = Task(
    description="""
    Fill in the phone number input field:
    
    1. Wait briefly to ensure the phone input is fully loaded
    2. Find the input field with placeholder "Phone number"
    3. Fill in the phone number "4695695711"
    
    Use these tools in sequence:
    1. wait_tool - Wait 2 seconds for input to be fully interactive
    2. fill_input_tool - Fill the input using selector '[placeholder="Phone number"]'
    """,
    expected_output="""Successfully filled phone number into the input field""",
    agent=web_agent,
    task_callbacks=on_task_start
)

click_continue_after_phone = Task(
    description="""
    Press Enter key after entering phone number:
    
    1. Wait briefly for the input to be ready
    2. Press the Enter key to submit the phone number
    3. Wait briefly after pressing Enter to allow for any transitions
    
    Use these tools in sequence:
    1. wait_tool - Wait 2 seconds for input to be fully processed
    2. press_key_tool - Press the "Enter" key with selector '[placeholder="Phone number"]'
    3. wait_tool - Wait 2 seconds for next screen
    """,
    expected_output="""Successfully pressed Enter after phone number entry""",
    agent=web_agent,
    task_callbacks=on_task_start
)

get_otp_code = Task(
    description="""
    Get the OTP code from human input and fill it in:
    
    1. Wait briefly for the OTP input field to appear
    2. Ask the human user for the OTP code
    3. Find the input field with name="code"
    4. Fill in the provided OTP code
    
    Use these tools in sequence:
    1. wait_tool - Wait 2 seconds for OTP input to appear
    2. get_human_input_tool - Get the OTP code from user with prompt "Please enter the OTP code sent to your phone"
    3. fill_input_tool - Fill the input using selector 'input[name="code"]' with the provided OTP
    """,
    expected_output="""Successfully obtained OTP code from user and filled it into the input field""",
    agent=web_agent,
    task_callbacks=on_task_start
)

capture_screenshot = Task(
    description="""Capture a screenshot of the page current page""",
    expected_output="""A screenshot of the page should be captured and saved to a file""",
    agent=web_agent,
    task_callbacks=on_task_start
)

crew = Crew(
    agents=[web_agent],
    tasks=[
        navigate_to_instacart, 
        find_and_click_continue_with_phone,
        fill_phone_number,
        click_continue_after_phone,
        get_otp_code,
        capture_screenshot
    ],
    process=Process.sequential,
    planning=False,
)

result = crew.kickoff()

# Test the agent with the task
print("\nTask Results:")
for task in crew.tasks:
    print(f"\n{task.description}:")
    print(task.output)

print("\nFinal Crew's Response:")
print(result)
