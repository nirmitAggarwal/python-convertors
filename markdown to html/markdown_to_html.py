import markdown
import os
import argparse
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from markdown.extensions.toc import TocExtension
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
from weasyprint import HTML
from datetime import datetime

class TitleExtractor(Treeprocessor):
    def run(self, root):
        for child in root:
            if child.tag.startswith('h'):
                self.md.title = child.text
                break

class TitleExtractorExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(TitleExtractor(md), 'title_extractor', 0)

def convert_markdown_to_html(md_text, inline_css=None, syntax_highlight_style=None):
    extensions = [
        TitleExtractorExtension(),
        'fenced_code',
        TocExtension(toc_depth="2-3")
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

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML or PDF.")
    parser.add_argument("markdown_file", help="Path to the Markdown file to convert.")
    parser.add_argument("output_file", help="Path to save the output file (HTML or PDF).")
    parser.add_argument("--css", help="Optional CSS file to link in the HTML.", default=None)
    parser.add_argument("--inline-css", help="Optional inline CSS styles to include in the HTML.", default=None)
    parser.add_argument("--syntax-highlight", help="Syntax highlight style (default: default).", default="default")
    parser.add_argument("--metadata", help="Optional metadata in 'key:value' format.", nargs='*', default=None)
    args = parser.parse_args()

    if not os.path.isfile(args.markdown_file):
        print(f"Error: The file {args.markdown_file} does not exist.")
        exit(1)

    try:
        with open(args.markdown_file, 'r', encoding='utf-8') as file:
            md_text = file.read()
    except Exception as e:
        print(f"Error reading {args.markdown_file}: {e}")
        exit(1)

    inline_css = args.inline_css

    if args.css and os.path.isfile(args.css):
        try:
            with open(args.css, 'r', encoding='utf-8') as css_file:
                inline_css = css_file.read()
        except Exception as e:
            print(f"Error reading CSS file {args.css}: {e}")
            exit(1)

    title, full_html = convert_markdown_to_html(md_text, inline_css, args.syntax_highlight)

    if args.metadata:
        metadata_html = "\n".join([f'<meta name="{k.strip()}" content="{v.strip()}">' for k, v in (item.split(':') for item in args.metadata)])
        full_html = full_html.replace('</head>', f'{metadata_html}\n</head>')

    if args.output_file.lower().endswith('.html'):
        try:
            with open(args.output_file, 'w', encoding='utf-8') as file:
                file.write(full_html)
        except Exception as e:
            print(f"Error writing to {args.output_file}: {e}")
            exit(1)
        print(f"Conversion successful! HTML file saved as {args.output_file}")
    elif args.output_file.lower().endswith('.pdf'):
        try:
            HTML(string=full_html).write_pdf(args.output_file)
        except Exception as e:
            print(f"Error writing to {args.output_file}: {e}")
            exit(1)
        print(f"Conversion successful! PDF file saved as {args.output_file}")
    else:
        print(f"Error: Unsupported output file format. Please use .html or .pdf.")
        exit(1)

if __name__ == "__main__":
    main()
