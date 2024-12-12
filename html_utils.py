from bs4 import BeautifulSoup

def clean_html_file(file_path):
    # Read the original HTML content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Remove <script>, <style>, and <link> tags
    for tag_name in ['script', 'style', 'link']:
        for t in soup.find_all(tag_name):
            t.decompose()

    # Remove 'id' and 'class' attributes from all tags
    for tag in soup.find_all(True):
        if 'id' in tag.attrs:
            del tag.attrs['id']
        if 'class' in tag.attrs:
            del tag.attrs['class']

    # Convert the cleaned soup back to a string
    cleaned_html = str(soup)

    # Write the cleaned HTML back to the same file (overwrites original)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_html) 