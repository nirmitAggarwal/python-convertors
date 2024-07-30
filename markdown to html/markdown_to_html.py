import markdown
import os
import argparse
import yaml
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from markdown.extensions.toc import TocExtension
from pygments.formatters import HtmlFormatter
from weasyprint import HTML
import re
import importlib.util
from flask import Flask, render_template_string, request
import threading

class TitleExtractor(Treeprocessor):
    def run(self, root):
        for child in root:
            if child.tag.startswith('h'):
                self.md.title = child.text
                break

class TitleExtractorExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(TitleExtractor(md), 'title_extractor', 0)

class CustomHTMLProcessor(Treeprocessor):
    def __init__(self, md, custom_elements):
        super().__init__(md)
        self.custom_elements = custom_elements

    def run(self, root):
        for element, html in self.custom_elements.items():
            for node in root.iter():
                if node.tag == element:
                    node.tag = 'div'
                    node.set('class', html)

class CustomHTMLExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {'custom_elements': [{}, 'Custom HTML elements to replace']}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.treeprocessors.register(CustomHTMLProcessor(md, self.getConfig('custom_elements')), 'custom_html', 0)

class ShortcodeProcessor(Treeprocessor):
    def __init__(self, md, shortcodes):
        super().__init__(md)
        self.shortcodes = shortcodes

    def run(self, root):
        self.process_element(root)

    def process_element(self, element):
        if element.text:
            element.text = self.replace_shortcodes(element.text)
        if element.tail:
            element.tail = self.replace_shortcodes(element.tail)
        for child in element:
            self.process_element(child)

    def replace_shortcodes(self, text):
        for shortcode, replacement in self.shortcodes.items():
            text = re.sub(r'\[\[' + re.escape(shortcode) + r'\]\]', replacement, text)
        return text

class ShortcodeExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {'shortcodes': [{}, 'Shortcodes to replace']}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.treeprocessors.register(ShortcodeProcessor(md, self.getConfig('shortcodes')), 'shortcodes', 0)

def extract_metadata(md_text):
    if md_text.startswith('---'):
        end = md_text.find('---', 3)
        if end != -1:
            metadata = yaml.safe_load(md_text[3:end])
            md_text = md_text[end+3:]
            return metadata, md_text
    return {}, md_text

def convert_markdown_to_html(md_text, inline_css=None, syntax_highlight_style=None, custom_elements=None, shortcodes=None):
    extensions = [
        TitleExtractorExtension(),
        'fenced_code',
        TocExtension(toc_depth="2-3"),
        CustomHTMLExtension(custom_elements=custom_elements),
        ShortcodeExtension(shortcodes=shortcodes)
    ]
    md = markdown.Markdown(extensions=extensions)
    html = md.convert(md_text)
    title = getattr(md, 'title', 'Converted Markdown')
    css = f"<style>{inline_css}</style>" if inline_css else ''

    if syntax_highlight_style:
        css += f"<style>{HtmlFormatter(style=syntax_highlight_style).get_style_defs('.highlight')}</style>"

    return title, f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        {css}
    </head>
    <body>
        <div class="toc">{md.toc}</div>
        {html}
    </body>
    </html>
    """

def load_plugins(plugin_paths):
    plugins = []
    for path in plugin_paths:
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location("plugin", path)
            plugin = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin)
            if hasattr(plugin, 'process'):
                plugins.append(plugin.process)
    return plugins

def apply_plugins(md_text, plugins):
    for plugin in plugins:
        md_text = plugin(md_text)
    return md_text

def validate_file_path(file_path, description, must_exist=True):
    if must_exist and not os.path.isfile(file_path):
        raise argparse.ArgumentTypeError(f"{description} '{file_path}' does not exist.")
    return file_path

app = Flask(__name__)
md_file_path = None
css_content = None
syntax_highlight_style = None
custom_elements = None
shortcodes = None
plugins = []

@app.route('/')
def index():
    if not md_file_path:
        return "Markdown file not specified."
    try:
        with open(md_file_path, 'r', encoding='utf-8') as file:
            md_text = file.read()
    except Exception as e:
        return f"Error reading {md_file_path}: {e}"

    metadata, md_text = extract_metadata(md_text)
    md_text = apply_plugins(md_text, plugins)
    title, html_content = convert_markdown_to_html(md_text, css_content, syntax_highlight_style, custom_elements, shortcodes)
    return render_template_string(html_content)

def run_server():
    app.run(debug=True, use_reloader=False)

def main():
    global md_file_path, css_content, syntax_highlight_style, custom_elements, shortcodes, plugins

    parser = argparse.ArgumentParser(description="Convert Markdown to HTML or PDF.")
    parser.add_argument("markdown_file", type=lambda x: validate_file_path(x, "Markdown file"), help="Path to the Markdown file to convert.")
    parser.add_argument("output_file", help="Path to save the output file (HTML or PDF).")
    parser.add_argument("--css", type=lambda x: validate_file_path(x, "CSS file"), help="Optional CSS file to link in the HTML.", default=None)
    parser.add_argument("--inline-css", help="Optional inline CSS styles to include in the HTML.", default=None)
    parser.add_argument("--syntax-highlight", help="Syntax highlight style (default: default).", default="default")
    parser.add_argument("--metadata", help="Optional metadata in 'key:value' format.", nargs='*', default=None)
    parser.add_argument("--template", type=lambda x: validate_file_path(x, "Template file"), help="Optional custom HTML template file.", default=None)
    parser.add_argument("--custom-elements", help="Custom elements in 'element:class' format.", nargs='*', default=None)
    parser.add_argument("--shortcodes", help="Shortcodes in 'shortcode:replacement' format.", nargs='*', default=None)
    parser.add_argument("--plugins", type=lambda x: validate_file_path(x, "Plugin file"), help="Paths to custom plugin scripts.", nargs='*', default=None)
    parser.add_argument("--live-preview", action='store_true', help="Enable live preview server.")
    args = parser.parse_args()

    try:
        with open(args.markdown_file, 'r', encoding='utf-8') as file:
            md_file_path = args.markdown_file
    except Exception as e:
        print(f"Error reading {args.markdown_file}: {e}")
        exit(1)

    metadata, _ = extract_metadata(md_file_path)
    if args.metadata:
        for item in args.metadata:
            key, value = item.split(':')
            metadata[key.strip()] = value.strip()

    if args.plugins:
        plugins = load_plugins(args.plugins)

    custom_elements = {}
    if args.custom_elements:
        for item in args.custom_elements:
            element, class_name = item.split(':')
            custom_elements[element.strip()] = class_name.strip()

    shortcodes = {}
    if args.shortcodes:
        for item in args.shortcodes:
            shortcode, replacement = item.split(':')
            shortcodes[shortcode.strip()] = replacement.strip()

    css_content = args.inline_css

    if args.css:
        try:
            with open(args.css, 'r', encoding='utf-8') as css_file:
                css_content = css_file.read()
        except Exception as e:
            print(f"Error reading CSS file {args.css}: {e}")
            exit(1)

    if args.live_preview:
        server_thread = threading.Thread(target=run_server)
        server_thread.start()
        print(f"Live preview server started at http://127.0.0.1:5000")
        return

    title, full_html = convert_markdown_to_html(md_file_path, css_content, args.syntax_highlight, custom_elements, shortcodes)

    metadata_html = "\n".join([f'<meta name="{k}" content="{v}">' for k, v in metadata.items()])

    if args.template:
        try:
            with open(args.template, 'r', encoding='utf-8') as template_file:
                template = template_file.read()
                full_html = template.replace("{{content}}", full_html).replace("{{metadata}}", metadata_html)
        except Exception as e:
            print(f"Error reading template file {args.template}: {e}")
            exit(1)

    if args.output_file.endswith('.pdf'):
        HTML(string=full_html).write_pdf(args.output_file)
    else:
        try:
            with open(args.output_file, 'w', encoding='utf-8') as output_file:
                output_file.write(full_html)
            print(f"Converted HTML saved to {args.output_file}")
        except Exception as e:
            print(f"Error saving output file {args.output_file}: {e}")
            exit(1)

if __name__ == "__main__":
    main()
