from bs4 import BeautifulSoup

def clean_html_file(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove <script>, <style>, and <link> tags
    for tag_name in ['script', 'style', 'link']:
        for t in soup.find_all(tag_name):
            t.decompose()

    # Convert the cleaned soup back to a string
    cleaned_html = str(soup)
    return cleaned_html