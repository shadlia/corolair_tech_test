import requests
from io import BytesIO
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from fastapi import HTTPException
from PyPDF2 import PdfFileReader


def verify_pdf(url: str) -> bool:
    """
    Verifies that the URL points to a valid PDF file.
    Returns True if the file is a valid PDF, raises an HTTPException otherwise.
    """
    try:
        # Step 1: Request the file from the URL
        response = requests.get(url, stream=True)

        # Step 2: Check if the response is a PDF by verifying the content type
        if "pdf" not in response.headers.get("Content-Type", "").lower():
            raise ValueError("The document is not a valid PDF.")

        # Step 3: Try reading the PDF content using PyPDF2
        pdf_file = BytesIO(response.content)
        pdf_reader = PdfFileReader(pdf_file)

        # If no pages are found, it's not a valid PDF
        if pdf_reader.numPages < 1:
            raise ValueError("The PDF file is empty or invalid.")

        return True
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid PDF file: {str(e)}")


def process_pdf(pdf_file):
    """
    Processes a PDF file and extracts text chunks.
    Returns a list of text chunks from the PDF.
    """
    try:
        # Step 1: Load the PDF and convert to documents
        loader = PyMuPDFLoader(pdf_file)
        documents = loader.load()

        # Step 2: Chunk the document using RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        text_chunks = text_splitter.split_documents(documents)

        # Return only the content of the chunks
        return [chunk.page_content for chunk in text_chunks]

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
