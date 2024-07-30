import markdown
import sys
import os

def convert_markdown_to_html(md_text):
    html = markdown.markdown(md_text)
    return html

def generate_html_template(content):
    template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Converted Markdown</title>
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
    if len(sys.argv) != 3:
        print("Usage: python markdown_to_html_v2.py <markdown_file> <output_html_file>")
        sys.exit(1)

    markdown_file = sys.argv[1]
    output_html_file = sys.argv[2]

    if not os.path.isfile(markdown_file):
        print(f"Error: The file {markdown_file} does not exist.")
        sys.exit(1)

    try:
        with open(markdown_file, 'r', encoding='utf-8') as file:
            md_text = file.read()
    except Exception as e:
        print(f"Error reading {markdown_file}: {e}")
        sys.exit(1)

    html_content = convert_markdown_to_html(md_text)
    full_html = generate_html_template(html_content)

    try:
        with open(output_html_file, 'w', encoding='utf-8') as file:
            file.write(full_html)
    except Exception as e:
        print(f"Error writing to {output_html_file}: {e}")
        sys.exit(1)

    print(f"Conversion successful! HTML file saved as {output_html_file}")

if __name__ == "__main__":
    main()
