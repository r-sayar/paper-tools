from flask import Flask, request, send_file, render_template_string
import subprocess
import tempfile
import os

import uuid # For unique filenames
import requests
from dotenv import load_dotenv
load_dotenv()

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
            <input type="file" id="markdown_file" name="markdown_file" accept=".md,.markdown">
            <p style="text-align:center;">OR</p>
            <label for="markdown_text">Paste Markdown Text:</label>
            <textarea id="markdown_text" name="markdown_text" rows="10" style="width:100%;" placeholder="Paste your Markdown here..."></textarea>
            <input type="submit" value="Convert to PDF">
        </form>
        <form method="post" action="/download_related">
            <input type="hidden" name="markdown_text" id="hidden_markdown_text">
            <input type="submit" value="Download Related Articles as ZIP">
        </form>
        <script>
            document.querySelector('form[action="/download_related"]').addEventListener('submit', function(e) {
                document.getElementById('hidden_markdown_text').value = document.getElementById('markdown_text').value;
            });
        </script>
        {% if message %}
            <p class="message {{ 'error' if error else 'success' }}">{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

def generate_title_from_markdown(markdown_text):
    """
    Calls OpenAI API to generate a title for the given markdown content.
    Returns the generated title as a string, or None if it fails.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")

    # Limit the length of the markdown text to avoid overly long prompts
    if len(markdown_text) > 500:
        markdown_text = markdown_text[:500] + "..."

    prompt = (
        "Given the following Markdown content, generate a concise and relevant title for it:\n\n"
        f"{markdown_text}\n\nTitle:"
    )

    try:
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo-instruct",
                "prompt": prompt,
                "max_tokens": 16,
                "temperature": 0.7,
                "n": 1,
                "stop": ["\n"]
            }
        )
        response.raise_for_status()
        data = response.json()
        title = data["choices"][0]["text"].strip()
        return title
    except Exception as e:
        print(f"Error generating title: {e}")
        return None

@app.route('/', methods=['GET'])
def index():
        return render_template_string(HTML_FORM)

@app.route('/convert', methods=['POST'])
def convert_markdown_to_pdf():
        if 'markdown_file' not in request.files and 'markdown_text' not in request.form:
                return render_template_string(HTML_FORM, message="No file or text part in the request.", error=True), 400
        
        file = request.files.get('markdown_file')
        markdown_text = request.form.get('markdown_text')

        if file and file.filename == '' and not markdown_text:
                return render_template_string(HTML_FORM, message="No file selected or text provided.", error=True), 400

        if file and (file.filename.lower().endswith('.md') or file.filename.lower().endswith('.markdown')):
                original_filename = file.filename
                
                # Use a temporary directory that cleans up automatically
                with tempfile.TemporaryDirectory() as temp_dir:
                        # Create unique filenames within the temporary directory
                        unique_id = uuid.uuid4().hex
                        base_name = "".join(c if c.isalnum() else '_' for c in original_filename).strip('_') # Basic sanitization
                        input_md_filename = f"{base_name}_{unique_id}.md"
                        output_pdf_filename = f"{base_name}_{unique_id}.pdf"

                        input_md_path = os.path.join(temp_dir, input_md_filename)
                        output_pdf_path = os.path.join(temp_dir, output_pdf_filename)

                        file.save(input_md_path)

                        try:
                                # Adjust this command if your markdown2pdf tool has different arguments
                                # Example: markdown2pdf input.md -o output.pdf
                                cmd = ['./markdown2pdf.py', input_md_path, output_pdf_path']
                                
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
        elif markdown_text:
                # Try to generate a title using AI
                ai_title = generate_title_from_markdown(markdown_text)
                original_filename = ai_title if ai_title else "pasted_markdown"
                
                # Use a temporary directory that cleans up automatically
                with tempfile.TemporaryDirectory() as temp_dir:
                        # Create unique filenames within the temporary directory
                        unique_id = uuid.uuid4().hex
                        base_name = "".join(c if c.isalnum() else '_' for c in original_filename).strip('_') # Basic sanitization
                        input_md_filename = f"{base_name}_{unique_id}.md"
                        output_pdf_filename = f"{base_name}_{unique_id}.pdf"

                        input_md_path = os.path.join(temp_dir, input_md_filename)
                        output_pdf_path = os.path.join(temp_dir, output_pdf_filename)

                        with open(input_md_path, 'w') as f:
                                f.write(markdown_text)

                        try:
                                # Adjust this command if your markdown2pdf tool has different arguments
                                # Example: markdown2pdf input.md -o output.pdf
                                cmd = ['./markdown2pdf.py', input_md_path, output_pdf_path']
                                
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

@app.route('/download_related', methods=['POST'])
def download_related():
    markdown_text = request.form.get('markdown_text', '')
    if not markdown_text.strip():
        return render_template_string(HTML_FORM, message="Please paste Markdown text to find related articles.", error=True), 400

    with tempfile.TemporaryDirectory() as temp_dir:
        input_md_path = os.path.join(temp_dir, "input.md")
        output_zip_path = os.path.join(temp_dir, "related_articles.zip")
        with open(input_md_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        cmd = [
            './download-futurehouse-papers.py',
            input_md_path,
            output_zip_path
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode != 0 or not os.path.exists(output_zip_path):
            error_message = "Failed to download related articles as ZIP."
            if process.stderr:
                error_message += f" Details: {process.stderr[:500]}"
            return render_template_string(HTML_FORM, message=error_message, error=True), 500

        return send_file(
            output_zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name='related_articles.zip'
        )

if __name__ == '__main__':
        # For development only. In production, use a proper WSGI server.
        app.run(debug=True, host='0.0.0.0', port=5000)