from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set to True to run without UI
    page = browser.new_page()
    page.goto("https://www.google.com")

    print("Page title:", page.title())

    browser.close()
