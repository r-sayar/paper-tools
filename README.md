"""
This script provides utilities for paper tools, right now solely Markdown2PDF

**Markdown to PDF Conversion Prerequisites:**

To utilize the Markdown to PDF functionality, ensure you have the following dependencies installed:
1.  **fpdf2**: You must install `fpdf2`. This can typically be done via pip:
    ```
    bash
    pip install fpdf2
    bash
    pip install fpdf2
    ```

2.  **markdown**: You must install `markdown`. This can typically be done via pip:
    ```
    bash
    pip install markdown
    ``` 
3. create markdowncopypasta.md file 
4. in input create a config.ini which contains email: your-email #only if you need to download papers
**Command-Line Usage:**

This script can be executed from the command line. The general syntax is:
`python markdown2pdf.py [<input_markdown_file>] <output_pdf_file>`

**API Status:**

**Important Note:** The API functionality of this script is currently not working. We are aware of this issue.

**Future Enhancements:**

This script will be further modified and improved to enhance its usability and integration, particularly with Platform House.


**Using this in the CLI**
Type in any terminal: 
1. export PATH="$PATH:/path/to/this/folder/paper-tools"
2. chmod +x /path/to/this/folder/paper-tools/markdown2pdf.py
3. chmod +x /path/to/this/folder/paper-tools/download-futurehouse-papers.py
4. 
    nano ~/.zshrc #or nano ~/.bash_profile depending on your OS
    Add this line at the end (if not already present):
    export PATH="$PATH:/Users/rls/Desktop/programming-projects/paper-tools"
    Open new terminal:
        source ~/.zshrc
5. (optional) If you are using mac, you might need to add your Terminal to have System Wide Access. Ask a GPT on how to do that. 
"""


