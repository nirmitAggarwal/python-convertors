import html2text
import re
import logging
import configparser
import os
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox

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
            'ignore_code': 'False',
            'ignore_horizontal_rules': 'False',
            'ignore_lists': 'False',
            'ignore_divs_and_spans': 'False',
            'ignore_html5_elements': 'False',
            'ignore_forms': 'False',
            'ignore_details_summary': 'False',
            'body_width': '0'
        }
        with open(config_file, 'w') as configfile:
            config.write(configfile)
    return config

def html_to_markdown(html, config):
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
    h.ignore_code = config.getboolean('DEFAULT', 'ignore_code')
    h.ignore_horizontal_rules = config.getboolean('DEFAULT', 'ignore_horizontal_rules')
    h.ignore_lists = config.getboolean('DEFAULT', 'ignore_lists')
    h.ignore_divs_and_spans = config.getboolean('DEFAULT', 'ignore_divs_and_spans')
    h.ignore_html5_elements = config.getboolean('DEFAULT', 'ignore_html5_elements')
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
    markdown = handle_details_and_summary(markdown)
    markdown = handle_images_with_captions(markdown)

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
    # Convert basic form elements to Markdown
    form_md = re.sub(r'<input[^>]*>', 'Input Field', form_html)
    form_md = re.sub(r'<textarea[^>]*>(.*?)</textarea>', 'Text Area:\n\1', form_md, flags=re.DOTALL)
    form_md = re.sub(r'<button[^>]*>(.*?)</button>', 'Button: \1', form_md)
    return f'\n\nForm:\n{form_md}'

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

def handle_details_and_summary(markdown):
    logging.debug('Handling details and summary')
    details_pattern = re.compile(r'<details[^>]*>(.*?)</details>', re.DOTALL)
    summary_pattern = re.compile(r'<summary[^>]*>(.*?)</summary>', re.DOTALL)
    
    markdown = details_pattern.sub(lambda m: f'<details>\n{summary_pattern.sub(lambda s: f"### Summary: {s.group(1)}", m.group(1))}\n{summary_pattern.sub("", m.group(1))}\n</details>', markdown)
    return markdown

def handle_images_with_captions(markdown):
    logging.debug('Handling images with captions')
    img_pattern = re.compile(r'<figure>\s*<img[^>]*src="([^"]*)"[^>]*>\s*<figcaption>(.*?)</figcaption>\s*</figure>', re.DOTALL)
    markdown = img_pattern.sub(r'![\2](\1)', markdown)
    return markdown

# GUI Implementation using Tkinter
def select_input_file():
    input_file = filedialog.askopenfilename(filetypes=[("HTML files", "*.html"), ("All files", "*.*")])
    if input_file:
        input_file_entry.delete(0, tk.END)
        input_file_entry.insert(0, input_file)

def select_output_file():
    output_file = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md"), ("All files", "*.*")])
    if output_file:
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, output_file)

def convert_html_to_markdown():
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    config_file = config_file_entry.get()

    if not input_file or not output_file:
        messagebox.showerror("Error", "Please specify both input and output files")
        return

    config = load_config(config_file)

    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    markdown_content = html_to_markdown(html_content, config)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    messagebox.showinfo("Success", f'Conversion completed. Markdown saved to {output_file}')

def create_gui():
    root = tk.Tk()
    root.title("HTML to Markdown Converter")

    # Input file selection
    tk.Label(root, text="Input HTML File:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    global input_file_entry
    input_file_entry = tk.Entry(root, width=50)
    input_file_entry.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse...", command=select_input_file).grid(row=0, column=2, padx=10, pady=10)

    # Output file selection
    tk.Label(root, text="Output Markdown File:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    global output_file_entry
    output_file_entry = tk.Entry(root, width=50)
    output_file_entry.grid(row=1, column=1, padx=10, pady=10)
    tk.Button(root, text="Browse...", command=select_output_file).grid(row=1, column=2, padx=10, pady=10)

    # Config file selection
    tk.Label(root, text="Config File (optional):").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    global config_file_entry
    config_file_entry = tk.Entry(root, width=50)
    config_file_entry.grid(row=2, column=1, padx=10, pady=10)
    config_file_entry.insert(0, 'config.ini')

    # Convert button
    tk.Button(root, text="Convert", command=convert_html_to_markdown, width=20).grid(row=3, column=0, columnspan=3, pady=20)

    root.mainloop()

if __name__ == '__main__':
    create_gui()
