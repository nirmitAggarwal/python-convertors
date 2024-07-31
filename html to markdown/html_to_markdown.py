import html2text
import re
import logging

# Set up logging to output detailed information and errors to a file
logging.basicConfig(filename='html_to_markdown.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(message)s')

def html_to_markdown(html):
    """
    Convert HTML content to Markdown format.
    
    This function handles headings, paragraphs, bold, italic, links, images,
    blockquotes, lists, code blocks, horizontal rules, tables, inline styles,
    forms, divs, and spans.

    Args:
    html (str): HTML content as a string.

    Returns:
    str: Markdown formatted content.
    """
    logging.debug('Starting HTML to Markdown conversion')
    
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
        logging.debug('Initial conversion done')
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
    markdown = handle_forms(markdown)
    markdown = handle_divs_and_spans(markdown)

    logging.debug('HTML to Markdown conversion completed')
    return markdown

def handle_code_blocks(markdown):
    logging.debug('Handling code blocks')
    code_block_pattern = re.compile(r'<pre><code>(.*?)</code></pre>', re.DOTALL)
    markdown = code_block_pattern.sub(r'```\1```', markdown)
    return markdown

def handle_horizontal_rules(markdown):
    logging.debug('Handling horizontal rules')
    hr_pattern = re.compile(r'<hr\s*/?>', re.IGNORECASE)
    markdown = hr_pattern.sub(r'---', markdown)
    return markdown

def handle_lists(markdown):
    logging.debug('Handling lists')
    markdown = re.sub(r'<ul>(.*?)</ul>', handle_unordered_list, markdown, flags=re.DOTALL)
    markdown = re.sub(r'<ol>(.*?)</ol>', handle_ordered_list, markdown, flags=re.DOTALL)
    return markdown

def handle_unordered_list(match):
    logging.debug('Handling unordered list')
    items = re.findall(r'<li>(.*?)</li>', match.group(1), re.DOTALL)
    nested_ul = re.compile(r'<ul>(.*?)</ul>', re.DOTALL)
    nested_ol = re.compile(r'<ol>(.*?)</ol>', re.DOTALL)
    formatted_items = []
    for item in items:
        sub_items = []
        if nested_ul.search(item):
            sub_items.append(nested_ul.sub(handle_unordered_list, item))
        elif nested_ol.search(item):
            sub_items.append(nested_ol.sub(handle_ordered_list, item))
        else:
            sub_items.append(item.strip())
        formatted_items.append('- ' + '\n  '.join(sub_items))
    return '\n'.join(formatted_items)

def handle_ordered_list(match):
    logging.debug('Handling ordered list')
    items = re.findall(r'<li>(.*?)</li>', match.group(1), re.DOTALL)
    nested_ul = re.compile(r'<ul>(.*?)</ul>', re.DOTALL)
    nested_ol = re.compile(r'<ol>(.*?)</ol>', re.DOTALL)
    formatted_items = []
    for i, item in enumerate(items, start=1):
        sub_items = []
        if nested_ul.search(item):
            sub_items.append(nested_ul.sub(handle_unordered_list, item))
        elif nested_ol.search(item):
            sub_items.append(nested_ol.sub(handle_ordered_list, item))
        else:
            sub_items.append(item.strip())
        formatted_items.append(f'{i}. ' + '\n  '.join(sub_items))
    return '\n'.join(formatted_items)

def handle_blockquotes(markdown):
    logging.debug('Handling blockquotes')
    blockquote_pattern = re.compile(r'<blockquote>(.*?)</blockquote>', re.DOTALL)
    markdown = blockquote_pattern.sub(r'> \1', markdown)
    return markdown

def handle_tables(markdown):
    logging.debug('Handling tables')
    table_pattern = re.compile(r'<table>(.*?)</table>', re.DOTALL)
    markdown = table_pattern.sub(convert_table, markdown)
    return markdown

def convert_table(match):
    logging.debug('Converting table')
    table_html = match.group(1)
    rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.DOTALL)
    table_md = []
    for row in rows:
        cols = re.findall(r'<t[dh](?:[^>]*)>(.*?)</t[dh]>', row, re.DOTALL)
        table_md.append('| ' + ' | '.join(col.strip() for col in cols) + ' |')
    if table_md:
        header_separator = '| ' + ' | '.join(['---'] * len(cols)) + ' |'
        table_md.insert(1, header_separator)
    return '\n'.join(table_md)

def handle_inline_styles(markdown):
    logging.debug('Handling inline styles')
    style_pattern = re.compile(r'<span style=".*?">(.*?)</span>', re.DOTALL)
    markdown = style_pattern.sub(r'\1', markdown)
    
    # Handle additional inline styles
    markdown = re.sub(r'<span style="font-weight: bold;">(.*?)</span>', r'**\1**', markdown)
    markdown = re.sub(r'<span style="font-weight: normal;">(.*?)</span>', r'\1', markdown)
    markdown = re.sub(r'<span style="text-align: center;">(.*?)</span>', r'\n<center>\1</center>\n', markdown)
    markdown = re.sub(r'<span style="text-align: right;">(.*?)</span>', r'\n<div align="right">\1</div>\n', markdown)
    
    return markdown

def handle_forms(markdown):
    logging.debug('Handling forms')
    form_pattern = re.compile(r'<form[^>]*>(.*?)</form>', re.DOTALL)
    markdown = form_pattern.sub(convert_form, markdown)
    return markdown

def convert_form(match):
    logging.debug('Converting form')
    form_html = match.group(1)
    inputs = re.findall(r'<input[^>]*>', form_html)
    textareas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', form_html, re.DOTALL)
    buttons = re.findall(r'<button[^>]*>(.*?)</button>', form_html, re.DOTALL)

    form_md = []
    for input_tag in inputs:
        input_type = re.search(r'type="([^"]*)"', input_tag)
        input_name = re.search(r'name="([^"]*)"', input_tag)
        if input_type and input_name:
            form_md.append(f'Input: {input_name.group(1)} ({input_type.group(1)})')

    for textarea in textareas:
        form_md.append(f'Textarea: {textarea.strip()}')

    for button in buttons:
        form_md.append(f'Button: {button.strip()}')

    return '\n'.join(form_md)

def handle_divs_and_spans(markdown):
    """
    Handle conversion of <div> and <span> elements with various styles and attributes.
    
    Args:
    markdown (str): Markdown content as a string.

    Returns:
    str: Markdown content with <div> and <span> elements properly formatted.
    """
    logging.debug('Handling divs and spans')
    
    # Example: Simple conversion, can be extended to handle more attributes and styles
    div_pattern = re.compile(r'<div[^>]*>(.*?)</div>', re.DOTALL)
    span_pattern = re.compile(r'<span[^>]*>(.*?)</span>', re.DOTALL)
    
    markdown = div_pattern.sub(r'\1', markdown)
    markdown = span_pattern.sub(r'\1', markdown)
    
    return markdown

# Example HTML content for testing
html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML</title>
</head>
<body>
    <h1>Heading 1</h1>
    <p>This is a <strong>bold</strong> paragraph.</p>
    <p>This is an <em>italic</em> paragraph.</p>
    <p>This is a paragraph with a <a href="https://www.example.com">link</a>.</p>
    <p>This is an image: <img src="https://www.example.com/image.jpg" alt="Sample Image"></p>
    <blockquote>This is a blockquote.</blockquote>
    <pre><code>print("Hello, World!")</code></pre>
    <hr>
    <table>
        <tr>
            <th>Header 1</th>
            <th>Header 2</th>
        </tr>
        <tr>
            <td>Row 1, Cell 1</td>
            <td>Row 1, Cell 2</td>
        </tr>
        <tr>
            <td>Row 2, Cell 1</td>
            <td>Row 2, Cell 2</td>
        </tr>
    </table>
    <p>This is a <span style="font-weight: bold;">bold text</span>.</p>
    <p>This is a <span style="text-align: center;">centered text</span>.</p>
    <form action="/submit" method="post">
        <input type="text" name="username" placeholder="Username">
        <input type="password" name="password" placeholder="Password">
        <textarea name="message">Enter your message here</textarea>
        <button type="submit">Submit</button>
    </form>
    <div>
        <p>Inside a div</p>
        <span>Inside a span</span>
    </div>
    <ul>
        <li>First item
            <ul>
                <li>Nested item 1</li>
                <li>Nested item 2</li>
            </ul>
        </li>
        <li>Second item</li>
    </ul>
</body>
</html>
'''

markdown_content = html_to_markdown(html_content)
print(markdown_content)
