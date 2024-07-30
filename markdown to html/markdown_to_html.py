import markdown
import os
import argparse

def convert_markdown_to_html(md_text):
    html = markdown.markdown(md_text)
    return html

def generate_html_template(content, css_file=None):
    css_link = f'<link rel="stylesheet" type="text/css" href="{css_file}">' if css_file else ''
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Converted Markdown</title>
        {css_link}
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        {content}
    </body>
    </html>
    """
    return template

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML.")
    parser.add_argument("markdown_file", help="Path to the Markdown file to convert.")
    parser.add_argument("output_html_file", help="Path to save the output HTML file.")
    parser.add_argument("--css", help="Optional CSS file to link in the HTML.", default=None)
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

    html_content = convert_markdown_to_html(md_text)
    full_html = generate_html_template(html_content, args.css)

    try:
        with open(args.output_html_file, 'w', encoding='utf-8') as file:
            file.write(full_html)
    except Exception as e:
        print(f"Error writing to {args.output_html_file}: {e}")
        exit(1)

    print(f"Conversion successful! HTML file saved as {args.output_html_file}")

if __name__ == "__main__":
    main()
