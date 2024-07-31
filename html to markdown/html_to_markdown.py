import html2text
import re

def html_to_markdown(html):
    """
    Convert HTML content to Markdown format.
    
    This function handles headings, paragraphs, bold, italic, links, images,
    blockquotes, lists, code blocks, and horizontal rules.

    Args:
    html (str): HTML content as a string.

    Returns:
    str: Markdown formatted content.
    """
    # Create an instance of the HTML2Text converter
    h = html2text.HTML2Text()
    
    # Configuration options
    h.ignore_links = False  # Convert links
    h.ignore_images = False # Convert images
    h.ignore_emphasis = False # Convert emphasis (bold, italic)
    h.ignore_tables = False  # Convert tables (if needed in the future)
    h.ignore_anchors = False # Convert anchor tags
    h.ignore_blockquotes = False # Convert blockquotes
    h.body_width = 0  # Do not wrap text at all

    # Convert HTML to Markdown
    try:
        markdown = h.handle(html)
    except Exception as e:
        print(f"An error occurred while converting HTML to Markdown: {e}")
        return ""

    # Strip leading and trailing whitespace from the Markdown content
    markdown = markdown.strip()

    # Handle additional formatting manually
    markdown = handle_code_blocks(markdown)
    markdown = handle_horizontal_rules(markdown)
    markdown = handle_lists(markdown)
    markdown = handle_blockquotes(markdown)

    return markdown

def handle_code_blocks(markdown):
    """
    Handle conversion of code blocks.
    
    Args:
    markdown (str): Markdown content as a string.

    Returns:
    str: Markdown content with code blocks properly formatted.
    """
    code_block_pattern = re.compile(r'<pre><code>(.*?)</code></pre>', re.DOTALL)
    markdown = code_block_pattern.sub(r'```\1```', markdown)
    return markdown

def handle_horizontal_rules(markdown):
    """
    Handle conversion of horizontal rules.
    
    Args:
    markdown (str): Markdown content as a string.

    Returns:
    str: Markdown content with horizontal rules properly formatted.
    """
    hr_pattern = re.compile(r'<hr\s*/?>', re.IGNORECASE)
    markdown = hr_pattern.sub(r'---', markdown)
    return markdown

def handle_lists(markdown):
    """
    Handle conversion of ordered and unordered lists.
    
    Args:
    markdown (str): Markdown content as a string.

    Returns:
    str: Markdown content with lists properly formatted.
    """
    markdown = re.sub(r'<ul>(.*?)</ul>', handle_unordered_list, markdown, flags=re.DOTALL)
    markdown = re.sub(r'<ol>(.*?)</ol>', handle_ordered_list, markdown, flags=re.DOTALL)
    return markdown

def handle_unordered_list(match):
    """
    Helper function to handle unordered lists.
    
    Args:
    match (re.Match): Regex match object.

    Returns:
    str: Formatted unordered list.
    """
    items = re.findall(r'<li>(.*?)</li>', match.group(1), re.DOTALL)
    return '\n'.join([f'- {item.strip()}' for item in items])

def handle_ordered_list(match):
    """
    Helper function to handle ordered lists.
    
    Args:
    match (re.Match): Regex match object.

    Returns:
    str: Formatted ordered list.
    """
    items = re.findall(r'<li>(.*?)</li>', match.group(1), re.DOTALL)
    return '\n'.join([f'1. {item.strip()}' for item in items])

def handle_blockquotes(markdown):
    """
    Handle conversion of blockquotes.
    
    Args:
    markdown (str): Markdown content as a string.

    Returns:
    str: Markdown content with blockquotes properly formatted.
    """
    blockquote_pattern = re.compile(r'<blockquote>(.*?)</blockquote>', re.DOTALL)
    markdown = blockquote_pattern.sub(r'> \1', markdown)
    return markdown

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
    <p>Check out this <a href="https://example.com">link</a> and this image:</p>
    <img src="https://via.placeholder.com/150" alt="Sample Image">
    <blockquote>This is a blockquote example.</blockquote>
    <pre><code>print('Hello, world!')</code></pre>
    <hr>
    <ul>
        <li>First item</li>
        <li>Second item</li>
        <li>Third item</li>
    </ul>
    <ol>
        <li>First item</li>
        <li>Second item</li>
        <li>Third item</li>
    </ol>
</body>
</html>
'''

# Convert the example HTML to Markdown
markdown_content = html_to_markdown(html_content)

# Print the converted Markdown content
print(markdown_content)
