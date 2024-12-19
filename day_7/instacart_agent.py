from crewai import Agent, Task, LLM, Crew, Process
from crewai.tools import BaseTool
from litellm import completion
import json
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from typing import Optional, Any
from pydantic import Field, BaseModel
from bs4 import BeautifulSoup
from html_utils import clean_html_file
from dataclasses import dataclass
from login_tasks import get_login_with_phone_tasks, get_login_with_email_tasks

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

class NavigateTool(BaseTool):
    name: str = "navigate"
    description: str = "Navigates to a specified URL in the opened browser"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, url: str) -> str:
        """Navigates to a specified URL"""
        if not self.page:
            print("Browser is not opened. Please open browser first.")
            return "Browser is not opened. Please open browser first."
        self.page.goto(url)
        print(f"Navigated to {url} successfully")
        return f"Navigated to {url} successfully"

class GetHtmlTool(BaseTool):
    name: str = "get_html"
    description: str = "Gets the HTML from the current page and cleans it"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, file_path: str, context: list = None) -> str:
        """Gets the HTML from the current page and cleans it"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        html_content = self.page.content()
        return clean_html_file(html_content)

class SaveHtmlTool(BaseTool):
    name: str = "save_html"
    description: str = "Saves the HTML content to a specified file path"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, file_path: str) -> str:
        """Saves the HTML content to a specified file path"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        html_content = self.page.content()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(clean_html_file(html_content))
        
        return f"HTML content saved to {file_path}"

class FillInputTool(BaseTool):
    name: str = "fill_input"
    description: str = "Fills an input element identified by a selector with specified text"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, selector: str, text: str) -> str:
        """Fills an input element with text"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            self.page.fill(selector, text)
            return f"Successfully filled input {selector} with text: {text}"
        except Exception as e:
            return f"Error filling input: {str(e)}"

class ClickElementTool(BaseTool):
    name: str = "click_element"
    description: str = "Clicks an element identified by a selector"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, selector: str) -> str:
        """Clicks an element"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            self.page.click(selector)
            return f"Successfully clicked element: {selector}"
        except Exception as e:
            return f"Error clicking element: {str(e)}"

class ScreenshotTool(BaseTool):
    name: str = "take_screenshot"
    description: str = "Takes a screenshot of the current page or a specific element"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, file_path: str, selector: str = None) -> str:
        """Takes a screenshot and saves it to the specified path"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            if selector:
                element = self.page.locator(selector)
                element.screenshot(path=file_path)
                return f"Successfully captured screenshot of element {selector} to {file_path}"
            else:
                self.page.screenshot(path=file_path)
                return f"Successfully captured full page screenshot to {file_path}"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"

class PressKeyTool(BaseTool):
    name: str = "press_key"
    description: str = "Simulates pressing a keyboard key on the currently focused element"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, key: str, selector: str = None) -> str:
        """Presses a keyboard key"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            if selector:
                self.page.focus(selector)
            self.page.keyboard.press(key)
            return f"Successfully pressed {key} key"
        except Exception as e:
            return f"Error pressing key: {str(e)}"

class WaitTool(BaseTool):
    name: str = "wait"
    description: str = "Waits for a specified duration in milliseconds"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, duration_ms: int = 2000) -> str:
        """Waits for the specified duration in milliseconds"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            self.page.wait_for_timeout(duration_ms)
            return f"Successfully waited for {duration_ms}ms"
        except Exception as e:
            return f"Error while waiting: {str(e)}"

class ClickButtonWithTextTool(BaseTool):
    name: str = "click_button_with_text"
    description: str = "Finds and clicks a button or element by its text content"
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self, text: str) -> str:
        """Finds an element by text and clicks it"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            element = self.page.get_by_text(text)
            element.wait_for(state='visible')
            box = element.bounding_box()
            if not box:
                return f"Element with text '{text}' not found or not visible"
            
            print(f"Found button at coordinates: x={box['x']}, y={box['y']}")
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
    page: Optional[Any] = Field(default=None)
    
    def __init__(self, page):
        super().__init__(page=page)
    
    def _run(self) -> str:
        """Finds and clicks the Continue button after phone number entry"""
        if not self.page:
            return "Browser is not opened. Please open browser first."
        
        try:
            button = self.page.locator('button:has-text("Continue"):right-of([placeholder="Phone number"])')
            button.wait_for(state='visible')
            box = button.bounding_box()
            if not box:
                return "Continue button not found or not visible"
            
            print(f"Found Continue button at coordinates: x={box['x']}, y={box['y']}")
            button.click()
            
            return f"Successfully clicked Continue button at coordinates x={box['x']}, y={box['y']}"
        except Exception as e:
            return f"Error finding or clicking Continue button: {str(e)}"

@dataclass
class InstacartState:
    """Represents the current state of the Instacart automation"""
    is_logged_in: bool = False
    phone_number: str = ""
    otp_code: str = ""
    current_page: str = ""
    playwright: Optional[Any] = None
    browser: Optional[Any] = None
    page: Optional[Any] = None

class InstacartFlow:
    """Custom flow class to manage Instacart automation"""
    
    def __init__(self):
        self.state = InstacartState()
        self.tools = []
        self.web_agent = None
        self.selector_agent = None
        self.crew = None

    def initialize(self):
        """Initialize browser, tools, and agents"""
        # Initialize browser
        self.state.playwright = sync_playwright().start()
        self.state.browser = self.state.playwright.chromium.launch(headless=False)
        self.state.page = self.state.browser.new_page()
        
        # Initialize tools
        self.tools = [
            NavigateTool(self.state.page),
            GetHtmlTool(self.state.page),
            SaveHtmlTool(self.state.page),
            FillInputTool(self.state.page),
            ClickElementTool(self.state.page),
            ClickButtonWithTextTool(self.state.page),
            ScreenshotTool(self.state.page),
            PressKeyTool(self.state.page),
            WaitTool(self.state.page),
            GetHumanInputTool(),
            ClickContinueAfterPhoneTool(self.state.page)
        ]

        # Initialize agents
        self.web_agent = Agent(
            role='Web Navigator',
            goal='Navigate and interact with web pages',
            backstory="Web automation expert capable of browsing websites",
            tools=self.tools,
            verbose=True,
            llm=llm,
            memory=True
        )

        # Create tasks


        # Initialize crew
        self.crew = Crew(
            agents=[self.web_agent],
            tasks=get_login_with_email_tasks(web_agent=self.web_agent),
            process=Process.sequential,
            planning=False
        )

    def run(self):
        """Execute the automation flow"""
        try:
            self.initialize()
            result = self.crew.kickoff()
            return result
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if self.state.page:
            self.state.page.close()
        if self.state.browser:
            self.state.browser.close()
        if self.state.playwright:
            self.state.playwright.stop()

def run_instacart_automation():
    flow = InstacartFlow()
    result = flow.run()
    return result

if __name__ == "__main__":
    result = run_instacart_automation()
    print("Automation Result:", result)
