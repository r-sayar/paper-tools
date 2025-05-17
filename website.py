

from flask import Flask, request, send_file, render_template_string
import subprocess
import tempfile
import os

import uuid # For unique filenames

app = Flask(__name__)

# HTML template for the upload form
HTML_FORM = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Markdown to PDF Converter</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; color: #333; display: flex; justify-content: center; align-items: center; min-height: 90vh; }
        .container { background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 100%; max-width: 500px; }
        h1 { color: #333; text-align: center; margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; }
        input[type="file"] { 
                display: block; 
                width: calc(100% - 22px); 
                padding: 10px; 
                margin-bottom: 20px; 
                border: 1px solid #ddd; 
                border-radius: 4px;
                box-sizing: border-box; 
        }
        input[type="submit"] { 
                background-color: #007bff; 
                color: white; 
                padding: 12px 20px; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                font-size: 16px;
                width: 100%;
                box-sizing: border-box;
        }
        input[type="submit"]:hover { background-color: #0056b3; }
        .message { padding: 10px; margin-top: 20px; border-radius: 4px; text-align: center; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Markdown to PDF</h1>
        <form method="post" enctype="multipart/form-data" action="/convert">
            <label for="markdown_file">Upload Markdown File:</label>
            <input type="file" id="markdown_file" name="markdown_file" accept=".md,.markdown" required>
            <input type="submit" value="Convert to PDF">
        </form>
        {% if message %}
            <p class="message {{ 'error' if error else 'success' }}">{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
        return render_template_string(HTML_FORM)

@app.route('/convert', methods=['POST'])
def convert_markdown_to_pdf():
        if 'markdown_file' not in request.files:
                return render_template_string(HTML_FORM, message="No file part in the request.", error=True), 400
        
        file = request.files['markdown_file']
        if file.filename == '':
                return render_template_string(HTML_FORM, message="No file selected.", error=True), 400

        if file and (file.filename.lower().endswith('.md') or file.filename.lower().endswith('.markdown')):
                original_filename = file.filename
                
                # Use a temporary directory that cleans up automatically
                with tempfile.TemporaryDirectory() as temp_dir:
                        # Create unique filenames within the temporary directory
                        unique_id = uuid.uuid4().hex
                        base_name = "".join(c if c.isalnum() else '_' for c in os.path.splitext(original_filename)[0]) # Basic sanitization
                        input_md_filename = f"{base_name}_{unique_id}.md"
                        output_pdf_filename = f"{base_name}_{unique_id}.pdf"

                        input_md_path = os.path.join(temp_dir, input_md_filename)
                        output_pdf_path = os.path.join(temp_dir, output_pdf_filename)

                        file.save(input_md_path)

                        try:
                                # Adjust this command if your markdown2pdf tool has different arguments
                                # Example: markdown2pdf input.md -o output.pdf
                                cmd = ['/Users/rls/Desktop/programming-projects/paper-tools/markdown2pdf.py', input_md_path, output_pdf_path]
                                
                                # If you were using Pandoc, it would be:
                                # cmd = ['pandoc', input_md_path, '-o', output_pdf_path]

                                process = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30) # Added timeout
                                
                                if process.returncode != 0:
                                        error_message = f"PDF generation failed (exit code {process.returncode})."
                                        if process.stderr:
                                                error_message += f" Details: {process.stderr[:500]}" # Limit error message length
                                        if process.stdout: # Sometimes errors go to stdout
                                                error_message += f" Stdout: {process.stdout[:500]}"
                                        return render_template_string(HTML_FORM, message=error_message, error=True), 500

                                if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 0:
                                        return send_file(
                                                output_pdf_path,
                                                as_attachment=True,
                                                download_name=os.path.splitext(original_filename)[0] + '.pdf',
                                                mimetype='application/pdf'
                                        )
                                else:
                                        error_message = "PDF generation failed: Output file not found or is empty."
                                        if process.stderr: error_message += f" stderr: {process.stderr[:500]}"
                                        if process.stdout: error_message += f" stdout: {process.stdout[:500]}"
                                        return render_template_string(HTML_FORM, message=error_message, error=True), 500

                        except subprocess.TimeoutExpired:
                                return render_template_string(HTML_FORM, message="PDF generation timed out after 30 seconds.", error=True), 500
                        except FileNotFoundError:
                                return render_template_string(HTML_FORM, message="markdown2pdf command not found. Make sure it's installed and in your PATH.", error=True), 500
                        except Exception as e:
                                return render_template_string(HTML_FORM, message=f"An unexpected error occurred: {str(e)}", error=True), 500
        else:
                return render_template_string(HTML_FORM, message="Invalid file type. Please upload a .md or .markdown file.", error=True), 400

if __name__ == '__main__':
        # For development only. In production, use a proper WSGI server.
        app.run(debug=True, host='0.0.0.0', port=5000)