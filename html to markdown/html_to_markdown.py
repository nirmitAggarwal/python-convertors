import html2text
import re
import logging

# Set up logging to output errors to a file
logging.basicConfig(filename='html_to_markdown.log', level=logging.ERROR)

def html_to_markdown(html):
    """
    Convert HTML content to Markdown format.
    
    This function handles headings, paragraphs, bold, italic, links, images,
    blockquotes, lists, code blocks, horizontal rules, tables, and inline styles.

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
    h.ignore_tables = False  # Convert tables
    h.ignore_anchors = False # Convert anchor tags
    h.ignore_blockquotes = False # Convert blockquotes
    h.body_width = 0  # Do not wrap text at all

    # Convert HTML to Markdown
    try:
        markdown = h.handle(html)
    except Exception as e:
        logging.error(f"An error occurred while converting HTML to Markdown: {e}")
        return ""

    # Strip leading and trailing whitespace from the Markdown content
    markdown = markdown.strip()

    # Handle additional formatting manually
    markdown = handle_code_blocks(markdown)
    markdown = handle_horizontal_rules(markdown)
    markdown = handle_lists(markdown)
    markdown = handle_blockquotes(markdown)
    markdown = handle_tables(markdown)
    markdown = handle_inline_styles(markdown)

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

def handle_tables(markdown):
    """
    Handle conversion of tables.
    
    Args:
    markdown (str): Markdown content as a string.

    Returns:
    str: Markdown content with tables properly formatted.
    """
    table_pattern = re.compile(r'<table>(.*?)</table>', re.DOTALL)
    markdown = table_pattern.sub(convert_table, markdown)
    return markdown

def convert_table(match):
    """
    Helper function to convert HTML tables to Markdown format.
    
    Args:
    match (re.Match): Regex match object.

    Returns:
    str: Formatted table in Markdown.
    """
    table_html = match.group(1)
    rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
    table_md = []
    for row in rows:
        cols = re.findall(r'<t[dh]>(.*?)</t[dh]>', row, re.DOTALL)
        table_md.append('| ' + ' | '.join(col.strip() for col in cols) + ' |')
    if table_md:
        header_separator = '| ' + ' | '.join(['---'] * len(cols)) + ' |'
        table_md.insert(1, header_separator)
    return '\n'.join(table_md)

def handle_inline_styles(markdown):
    """
    Handle conversion of inline styles (such as color and font size).
    
    Args:
    markdown (str): Markdown content as a string.

    Returns:
    str: Markdown content with inline styles properly formatted.
    """
    style_pattern = re.compile(r'<span style=".*?">(.*?)</span>', re.DOTALL)
    markdown = style_pattern.sub(r'\1', markdown)
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
    <table>
        <tr>
            <th>Header 1</th>
            <th>Header 2</th>
        </tr>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
        </tr>
        <tr>
            <td>Data 3</td>
            <td>Data 4</td>
        </tr>
    </table>
    <p><span style="color: red; font-size: 14px;">Styled text</span></p>
</body>
</html>
'''

# Convert the example HTML to Markdown
markdown_content = html_to_markdown(html_content)

# Print the converted Markdown content
print(markdown_content)
