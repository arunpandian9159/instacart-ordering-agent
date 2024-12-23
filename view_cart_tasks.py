
        # Task(
        #     description="""
        #     Click the View Cart button:
            
        #     1. Wait briefly for the add animation to complete
        #     2. Find and click the View Cart button
        #     3. Wait briefly for the cart dialog to open
            
        #     Use these tools in sequence:
        #     1. wait_tool - Wait 2 seconds for add animation
        #     2. click_button_tool - Click button with selector '[aria-label^="View Cart"]'
        #     3. wait_tool - Wait 3 seconds for cart dialog
        #     """,
        #     expected_output="""Successfully clicked View Cart button and opened cart dialog""",
        #     agent=web_agent,
        # ),