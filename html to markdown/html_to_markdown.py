import html2text
import re
import logging
import configparser
import os

# Set up logging to output detailed information and errors to a file
logging.basicConfig(filename='html_to_markdown.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(message)s')

def load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        config['DEFAULT'] = {
            'ignore_links': 'False',
            'ignore_images': 'False',
            'ignore_emphasis': 'False',
            'ignore_tables': 'False',
            'ignore_anchors': 'False',
            'ignore_blockquotes': 'False',
            'body_width': '0'
        }
        with open(config_file, 'w') as configfile:
            config.write(configfile)
    return config

def html_to_markdown(html, config):
    """
    Convert HTML content to Markdown format.
    
    This function handles headings, paragraphs, bold, italic, links, images,
    blockquotes, lists, code blocks, horizontal rules, tables, inline styles,
    forms, divs, spans, and HTML5 semantic elements.

    Args:
    html (str): HTML content as a string.
    config (ConfigParser): Configuration options for the conversion.

    Returns:
    str: Markdown formatted content.
    """
    logging.debug('Starting HTML to Markdown conversion')
    
    # Create an instance of the HTML2Text converter
    h = html2text.HTML2Text()
    
    # Apply configuration options
    h.ignore_links = config.getboolean('DEFAULT', 'ignore_links')
    h.ignore_images = config.getboolean('DEFAULT', 'ignore_images')
    h.ignore_emphasis = config.getboolean('DEFAULT', 'ignore_emphasis')
    h.ignore_tables = config.getboolean('DEFAULT', 'ignore_tables')
    h.ignore_anchors = config.getboolean('DEFAULT', 'ignore_anchors')
    h.ignore_blockquotes = config.getboolean('DEFAULT', 'ignore_blockquotes')
    h.body_width = config.getint('DEFAULT', 'body_width')

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
    markdown = handle_html5_semantic_elements(markdown)

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
    logging.debug('Handling divs and spans')
    div_pattern = re.compile(r'<div[^>]*>(.*?)</div>', re.DOTALL)
    span_pattern = re.compile(r'<span[^>]*>(.*?)</span>', re.DOTALL)
    markdown = div_pattern.sub(r'\1', markdown)
    markdown = span_pattern.sub(r'\1', markdown)
    return markdown

def handle_html5_semantic_elements(markdown):
    logging.debug('Handling HTML5 semantic elements')
    markdown = re.sub(r'<article[^>]*>(.*?)</article>', r'\1', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<section[^>]*>(.*?)</section>', r'\1', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<nav[^>]*>(.*?)</nav>', r'\1', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<aside[^>]*>(.*?)</aside>', r'\1', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<header[^>]*>(.*?)</header>', r'\1', markdown, flags=re.DOTALL)
    markdown = re.sub(r'<footer[^>]*>(.*?)</footer>', r'\1', markdown, flags=re.DOTALL)
    return markdown

# Load the configuration file
config = load_config()

# Example HTML content
html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test HTML</title>
</head>
<body>
    <header>
        <h1>HTML to Markdown Converter</h1>
    </header>
    <nav>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
    <section>
        <article>
            <h2>Introduction</h2>
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
        </article>
    </section>
    <aside>
        <p>Aside content here.</p>
    </aside>
    <footer>
        <p>Footer content here.</p>
    </footer>
</body>
</html>
'''

markdown_content = html_to_markdown(html_content, config)
print(markdown_content)
