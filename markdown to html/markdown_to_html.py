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
            spec = __import__(os.path.splitext(os.path.basename(path))[0])
            if hasattr(spec, 'process'):
                plugins.append(spec.process)
    return plugins

def apply_plugins(md_text, plugins):
    for plugin in plugins:
        md_text = plugin(md_text)
    return md_text

def validate_file_path(file_path, description, must_exist=True):
    if must_exist and not os.path.isfile(file_path):
        raise argparse.ArgumentTypeError(f"{description} '{file_path}' does not exist.")
    return file_path

def main():
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
    args = parser.parse_args()

    try:
        with open(args.markdown_file, 'r', encoding='utf-8') as file:
            md_text = file.read()
    except Exception as e:
        print(f"Error reading {args.markdown_file}: {e}")
        exit(1)

    metadata, md_text = extract_metadata(md_text)
    if args.metadata:
        for item in args.metadata:
            key, value = item.split(':')
            metadata[key.strip()] = value.strip()

    if args.plugins:
        plugins = load_plugins(args.plugins)
        md_text = apply_plugins(md_text, plugins)

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

    inline_css = args.inline_css

    if args.css:
        try:
            with open(args.css, 'r', encoding='utf-8') as css_file:
                inline_css = css_file.read()
        except Exception as e:
            print(f"Error reading CSS file {args.css}: {e}")
            exit(1)

    title, full_html = convert_markdown_to_html(md_text, inline_css, args.syntax_highlight, custom_elements, shortcodes)

    metadata_html = "\n".join([f'<meta name="{k}" content="{v}">' for k, v in metadata.items()])

    if args.template:
        try:
            with open(args.template, 'r', encoding='utf-8') as template_file:
                template = template_file.read()
                full_html = template.replace("{{title}}", title).replace("{{metadata}}", metadata_html).replace("{{content}}", full_html)
        except Exception as e:
            print(f"Error reading template file {args.template}: {e}")
            exit(1)
    else:
        full_html = full_html.replace('</head>', f'{metadata_html}\n</head>')

    output_dir = os.path.dirname(args.output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        if args.output_file.lower().endswith('.html'):
            with open(args.output_file, 'w', encoding='utf-8') as file:
                file.write(full_html)
            print(f"Conversion successful! HTML file saved as {args.output_file}")
        elif args.output_file.lower().endswith('.pdf'):
            HTML(string=full_html).write_pdf(args.output_file)
            print(f"Conversion successful! PDF file saved as {args.output_file}")
        else:
            raise ValueError("Unsupported output file format. Please use .html or .pdf.")
    except Exception as e:
        print(f"Error writing to {args.output_file}: {e}")
        exit(1)

if __name__ == "__main__":
    main()
