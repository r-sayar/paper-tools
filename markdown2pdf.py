#!/usr/bin/env python3.11

import markdown
from fpdf import FPDF
import sys
import os
import tempfile

def markdown_to_pdf(input_file, output_file):
    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as file:
        markdown_content = file.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content)

    # Create a PDF instance
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.add_font('ArialUnicode', '', '/Library/Fonts/Arial Unicode.ttf', uni=True)
    pdf.set_font('ArialUnicode', '', 12)
    # Add HTML content to the PDF
    # The FPDF.write_html method is basic and may not support all HTML tags or CSS.
    # For complex HTML, a more robust library might be needed.
    pdf.write_html(html_content)

    # Save the PDF to the output file
    pdf.output(output_file)

if __name__ == "__main__":
    #if len(sys.argv) < 2:
     #   input_file = "markdowncopypasta"
      #  output_file = sys.argv[1] if len(sys.argv) == 2 else "output.pdf"
    if len(sys.argv) == 1: 
        print("Paste your Markdown content below. Press Ctrl-D (Ctrl-Z on Windows) when done:")
        markdown_content = sys.stdin.read()

        downloads_folder = os.path.expanduser("~/Downloads")
        title = input("Enter a title for your PDF (without extension): ").strip() or "output"
        output_file = os.path.join(downloads_folder, f"{title}.pdf")
        input_file = None  # Not used in this mode

        # Write the markdown content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8") as tmp:
            tmp.write(markdown_content)
            tmp_path = tmp.name

        input_file = tmp_path

    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage: markdown2pdf.py [<input_markdown_file>] <output_pdf_file>")
        sys.exit(1)


    markdown_to_pdf(input_file, output_file)
    print(f"PDF generated: {output_file}")