import html2text

def html_to_markdown(html):
    """
    Convert HTML content to Markdown format.

    Args:
    html (str): HTML content as a string.

    Returns:
    str: Markdown formatted content.
    """
    # Create an instance of the HTML2Text converter
    h = html2text.HTML2Text()
    
    # Configuration options
    h.ignore_links = False  # Set to True if you want to ignore converting links
    h.ignore_images = False # Set to True if you want to ignore converting images
    h.ignore_emphasis = False # Set to True if you want to ignore converting emphasis (bold, italic)
    
    # Convert HTML to Markdown
    try:
        markdown = h.handle(html)
    except Exception as e:
        print(f"An error occurred while converting HTML to Markdown: {e}")
        return ""
    
    # Strip leading and trailing whitespace from the Markdown content
    return markdown.strip()

# Example HTML content for testing
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample HTML</title>
</head>
<body>
    <h1>Main Title</h1>
    <p>This is a <b>bold</b> and <i>italic</i> text example.</p>
    <h2>Subtitle</h2>
    <p>Another paragraph with <strong>strong</strong> and <em>emphasized</em> text.</p>
</body>
</html>
'''

# Convert the example HTML to Markdown
markdown_content = html_to_markdown(html_content)

# Print the converted Markdown content
print(markdown_content)
