import markdown
import sys

def convert_markdown_to_html(md_text):
    html = markdown.markdown(md_text)
    return html

def main():
    if len(sys.argv) != 2:
        print("Usage: python markdown_to_html.py <markdown_file>")
        sys.exit(1)

    markdown_file = sys.argv[1]

    try:
        with open(markdown_file, 'r', encoding='utf-8') as file:
            md_text = file.read()
    except FileNotFoundError:
        print(f"Error: The file {markdown_file} was not found.")
        sys.exit(1)

    html = convert_markdown_to_html(md_text)

    html_file = markdown_file.replace('.md', '.html')
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(html)
    
    print(f"Conversion successful! HTML file saved as {html_file}")

if __name__ == "__main__":
    main()
