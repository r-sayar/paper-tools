import os
import tempfile
import markdown2pdf
from weasyprint import HTML
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
import uvicorn

# Create a FastAPI app instance
app = FastAPI(
    title="Markdown to PDF Converter API",
    description="An API to convert Markdown text to a PDF file.",
    version="1.0.0",
)

def cleanup_temp_file(path: str):
    """Safely remove a temporary file."""
    try:
        os.remove(path)
    except OSError:
        # Log this in a real application (e.g., file not found, permissions error)
        pass

@app.post("/convert/markdown-to-pdf/")
async def convert_markdown_to_pdf(markdown_content: str = Body(..., embed=True, description="The Markdown content to convert.")):
    """
    Converts Markdown content to a PDF file.

    - **markdown_content**: The Markdown string to be converted.
    """
    if not markdown_content.strip():
        raise HTTPException(status_code=400, detail="Markdown content cannot be empty.")

    temp_pdf_path = None
    try:
        # Convert Markdown to HTML
        html_content = markdown2.markdown(markdown_content, extras=["fenced-code-blocks", "tables"])

        # Convert HTML to PDF using WeasyPrint
        pdf_bytes = HTML(string=html_content).write_pdf()

        # Create a temporary file to store the PDF.
        # We use delete=False because FileResponse needs to access the file by path.
        # The BackgroundTask will handle the deletion after the response is sent.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="markdown_api_") as temp_pdf_file_obj:
            temp_pdf_file_obj.write(pdf_bytes)
            temp_pdf_path = temp_pdf_file_obj.name

        return FileResponse(
            path=temp_pdf_path,
            media_type='application/pdf',
            filename='converted_document.pdf',
            background=BackgroundTask(cleanup_temp_file, temp_pdf_path)
        )
    except Exception as e:
        # If a temporary file was created before the exception occurred, try to clean it up.
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            cleanup_temp_file(temp_pdf_path)
        
        # Log the exception (in a real app, use a proper logger)
        print(f"Error during PDF conversion: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during PDF conversion: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "message": "Markdown to PDF Converter API is running.",
        "documentation": "/docs",
        "convert_endpoint": "/convert/markdown-to-pdf/ (POST)"
    }

if __name__ == "__main__":
    """
    To run this API:
    1. Save this file (e.g., as api.py).
    2. Install dependencies:
       pip install fastapi uvicorn python-multipart markdown2 weasyprint
       Note: WeasyPrint may have system-level dependencies (like Pango, Cairo, GDK-PixBuf).
       Refer to WeasyPrint documentation for installation details on your OS:
       https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation
    3. Run with Uvicorn from your terminal:
       uvicorn api:app --reload --host 0.0.0.0 --port 8000
    
    Or, if you run this script directly (python api.py), it will start the server.
    """
    print("Starting Markdown to PDF Converter API...")
    print("Dependencies: fastapi, uvicorn, python-multipart, markdown2, weasyprint")
    print("WeasyPrint might require system libraries. Check WeasyPrint docs if you encounter issues.")
    print("API will be available at http://localhost:8000")
    print("Swagger UI (documentation) at http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)