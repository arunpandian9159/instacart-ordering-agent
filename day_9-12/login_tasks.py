from crewai import Agent, Task, LLM, Crew, Process

def get_login_with_phone_tasks(web_agent):
    """
    Returns a list of tasks for logging into Instacart using phone number authentication.
    
    Args:
        web_agent: The web agent that will execute these tasks
        
    Returns:
        list[Task]: A list of sequential tasks for phone number login
    """
    tasks = [
        Task(
            description="Go to Instacart's Login https://instacart.com/login website",
            expected_output="""The browser should be opened and navigated to the Instacart website""",
            agent=web_agent,
        ),
        Task(
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
        ),
        Task(
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
        ),
        Task(
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
        ),
        Task(
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
        ),
        Task(
            description="""Capture a screenshot of the page current page""",
            expected_output="""A screenshot of the page should be captured and saved to a file""",
            agent=web_agent,
        )
    ]
    return tasks


def get_login_with_email_tasks(web_agent):
    """
    Returns a list of tasks for logging into Instacart using phone number authentication.
    
    Args:
        web_agent: The web agent that will execute these tasks
        
    Returns:
        list[Task]: A list of sequential tasks for phone number login
    """
    tasks = [
        Task(
            description="Go to Instacart's Login https://instacart.com/login website",
            expected_output="""The browser should be opened and navigated to the Instacart website""",
            agent=web_agent,
        ),
        Task(
            description="""
            Fill in the emauk input field:
            
            2. Find the input field with placeholder "Email"
            3. Fill in the email "peytoncas@gmail.com"
            
            Use these tools in sequence:
            1. wait_tool - Wait 2 seconds for input to be fully interactive
            2. fill_input_tool - Fill the input using selector '[placeholder="Email"]'
            """,
            expected_output="""Successfully filled phone number into the input field""",
            agent=web_agent,
        ),
        Task(
            description="""
            Press Enter key after entering email:
            
            1. Wait briefly for the input to be ready
            2. Press the Enter key to submit the email
            3. Wait briefly after pressing Enter to allow for any transitions
            
            Use these tools in sequence:
            1. wait_tool - Wait 2 seconds for input to be fully processed
            2. press_key_tool - Press the "Enter" key with selector '[placeholder="Email"]'
            3. wait_tool - Wait 2 seconds for next screen
            """,
            expected_output="""Successfully pressed Enter after email entry""",
            agent=web_agent,
        ),
        Task(
            description="""
            Get the OTP code from human input and fill it in:
            
            1. Wait briefly for the OTP input field to appear
            2. Ask the human user for the OTP code
            3. Find the input field with name="code"
            4. Fill in the provided OTP code
            
            Use these tools in sequence:
            1. wait_tool - Wait 2 seconds for OTP input to appear
            2. get_human_input_tool - Get the OTP code from user with prompt "Please enter the OTP code sent to your email"
            3. fill_input_tool - Fill the input using selector 'input[name="code"]' with the provided OTP
            """,
            expected_output="""Successfully obtained OTP code from user and filled it into the input field""",
            agent=web_agent,
        ),
        Task(
            description="""Capture a screenshot of the page current page""",
            expected_output="""A screenshot of the page should be captured and saved to a file""",
            agent=web_agent,
        )
    ]
    return tasks