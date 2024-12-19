from crewai import Agent, Task, LLM, Crew, Process

def search_for_item_tasks(web_agent):
    """
    Returns a list of tasks for logging into Instacart using phone number authentication.
    
    Args:
        web_agent: The web agent that will execute these tasks
        
    Returns:
        list[Task]: A list of sequential tasks for phone number login
    """
    tasks = [
        Task(
            description="""
            Fill in the search bar with the item "milk"
            
            1. Wait briefly to ensure the phone input is fully loaded
            2. Find the input field with placeholder "Search products, stores, and recipes"
            3. Fill in the phone number "milk"
            
            Use these tools in sequence:
            1. wait_tool - Wait 2 seconds for input to be fully interactive
            2. fill_input_tool - Fill the input using selector '[placeholder="Search products, stores, and recipes"]'
            """,
            expected_output="""Successfully filled search field with "milk" """,
            agent=web_agent,
        ),

        Task(
            description="""
            Press Enter key after entering search criteria:
            
            1. Wait briefly for the input to be ready
            2. Press the Enter key to search for the item
            3. Wait briefly after pressing Enter to allow for any transitions
            
            Use these tools in sequence:
            1. wait_tool - Wait 2 seconds for input to be fully processed
            2. press_key_tool - Press the "Enter" key with selector '[placeholder="Search products, stores, and recipes"]'
            3. wait_tool - Wait 2 seconds for next screen
            """,
            expected_output="""Successfully pressed Enter after phone number entry""",
            agent=web_agent,
        ),
        Task(
            description="""Capture a screenshot of the current page""",
            expected_output="""A screenshot of the page should be captured and saved to a file""",
            agent=web_agent,
        )
    ]
    return tasks
