from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # Navigate to Instacart login page
            print("Navigating to Instacart login...")
            page.goto('https://instacart.com/login')
            
            # Wait for page load
            # page.wait_for_load_state('networkidle')
            # Wait for initial page load
            print("Waiting for page to load...")
            # page.wait_for_load_state('networkidle')
            time.sleep(5)  # Additional wait to ensure full render
            
            # Find and click the "Continue with phone" button
            print("Looking for 'Continue with phone' button...")
            continue_with_phone = page.get_by_text("Continue with phone")
            
            # Wait to ensure button is visible and clickable
            continue_with_phone.wait_for(state='visible')
            
            # Get button coordinates (for debugging)
            box = continue_with_phone.bounding_box()
            print(f"Found button at coordinates: x={box['x']}, y={box['y']}")
            
            # Click the button
            print("Clicking 'Continue with phone' button...")
            continue_with_phone.click()
            
            # Wait to see the phone input field (adjust timeout as needed)
            print("Waiting for phone input field...")
            page.wait_for_timeout(2000)
            
            # Take a screenshot
            print("Taking screenshot...")
            page.screenshot(path="instacart_phone_input.png")
            
            # Wait a moment before closing
            time.sleep(5)
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            # Take screenshot on error for debugging
            page.screenshot(path="error_screenshot.png")
        
        finally:
            print("Closing browser...")
            browser.close()

if __name__ == "__main__":
    main()
