from crewai import Agent, Task, LLM, Crew, Process

def search_with_enter_tasks(web_agent, item="", button_selector='button[aria-label^="Add 1 item"]'):
    """
    Search for items using the Enter key method
    """
    tasks = [
        Task(
            description=f"""
            Fill in the search bar with the item "{item}"
            
            1. Wait briefly to ensure the phone input is fully loaded
            2. Find the input field with placeholder "Search products, stores, and recipes"
            3. Fill in the ingredient "{item}"
            
            Use these tools in sequence:
            1. wait_tool - Wait 5 seconds for input to be fully interactive
            2. fill_input_tool - Fill the input using selector '#search-bar-input'
            """,
            expected_output=f"""Successfully filled search field with "{item}" """,
            agent=web_agent,
        ),

        Task(
            description="""
            Press Enter key after entering search criteria:
            
            1. Wait briefly for the input to be ready
            2. Press the Enter key to search for the item
            3. Wait briefly after pressing Enter to allow for any transitions
            
            Use these tools in sequence:
            1. wait_tool - Wait 5 seconds for input to be fully processed
            2. press_key_tool - Press the "Enter" key with selector '#search-bar-input'
            3. wait_tool - Wait 5 seconds for search results
            """,
            expected_output="""Successfully pressed Enter after ingredient entry""",
            agent=web_agent,
        ),

        Task(
            description=f"""
            Click the Add button on the first matching item:
            
            1. Wait briefly for search results to load
            2. Find and click the Add button on the first product card
            3. Wait briefly after clicking to allow for any animations
            
            Use these tools in sequence:
            1. wait_tool - Wait 5 seconds for results to load
            2. click_button_tool - Click button with selector '{button_selector}'
            3. wait_tool - Wait 3 seconds for add animation
            """,
            expected_output="""Successfully clicked Add button on first matching item""",
            agent=web_agent,
        ),
        Task(
            description="""
            Refresh the page:
            
            1. Use the refresh tool to reload the current page
            2. Wait briefly after refresh to allow page to load
            
            Use these tools in sequence:
            1. refresh_tool - Refresh the current page
            2. wait_tool - Wait 5 seconds for page to reload
            """,
            expected_output="""Successfully refreshed the page""",
            agent=web_agent,
        ),

    ]
    return tasks

def search_with_click_tasks(web_agent, item="", button_selector='button[aria-label^="Add 1 item"]'):
    """
    Search for items by clicking the first autocomplete suggestion
    """
    tasks = [
        Task(
            description=f"""
            Fill in the search bar with the item "{item}"
            
            1. Wait briefly to ensure the phone input is fully loaded
            2. Find the input field with placeholder "Search products, stores, and recipes"
            3. Fill in the ingredient "{item}"
            
            Use these tools in sequence:
            1. wait_tool - Wait 5 seconds for input to be fully interactive
            2. fill_input_tool - Fill the input using selector '#search-bar-input'
            """,
            expected_output=f"""Successfully filled search field with "{item}" """,
            agent=web_agent,
        ),

        Task(
            description="""
            Click the first autocomplete suggestion:
            
            1. Wait briefly for autocomplete suggestions to appear
            2. Click the first suggestion in the dropdown
            3. Wait briefly after clicking to allow for page transition
            
            Use these tools in sequence:
            1. wait_tool - Wait 3 seconds for suggestions to appear
            2. click_button_tool - Click element with selector '#group-0-option-0'
            3. wait_tool - Wait 5 seconds for search results
            """,
            expected_output="""Successfully clicked first autocomplete suggestion""",
            agent=web_agent,
        ),

        Task(
            description=f"""
            Click the Add button on the first matching item:
            
            1. Wait briefly for search results to load
            2. Find and click the Add button on the first product card
            3. Wait briefly after clicking to allow for any animations
            
            Use these tools in sequence:
            1. wait_tool - Wait 5 seconds for results to load
            2. click_button_tool - Click button with selector '{button_selector}'
            3. wait_tool - Wait 3 seconds for add animation
            """,
            expected_output="""Successfully clicked Add button on first matching item""",
            agent=web_agent,
        ),
        Task(
            description="""
            Refresh the page:
            
            1. Use the refresh tool to reload the current page
            2. Wait briefly after refresh to allow page to load
            
            Use these tools in sequence:
            1. refresh_tool - Refresh the current page
            2. wait_tool - Wait 5 seconds for page to reload
            """,
            expected_output="""Successfully refreshed the page""",
            agent=web_agent,
        ),

    ]
    return tasks
