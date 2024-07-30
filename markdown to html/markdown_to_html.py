import markdown
import os
import argparse
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from weasyprint import HTML  # For PDF conversion

class TitleExtractor(Treeprocessor):
    def run(self, root):
        for child in root:
            if child.tag.startswith('h'):
                self.md.title = child.text
                break

class TitleExtractorExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(TitleExtractor(md), 'title_extractor', 0)

def convert_markdown_to_html(md_text, inline_css=None):
    md = markdown.Markdown(extensions=[TitleExtractorExtension()])
    html = md.convert(md_text)
    title = getattr(md, 'title', 'Converted Markdown')
    css = f"<style>{inline_css}</style>" if inline_css else ''
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

    title, full_html = convert_markdown_to_html(md_text, args.inline_css)

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
