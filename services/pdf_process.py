import requests
from io import BytesIO
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def process_pdf(pdf_file):
    """
    Processes a PDF file and extracts text chunks.
    Returns a list of text chunks from the PDF.
    """
    try:
        # Step 1 : Load the PDF and convert to documents
        loader = PyMuPDFLoader(pdf_file)
        documents = loader.load()

        # Step 2 : Chunk the document using RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        text_chunks = text_splitter.split_documents(documents)
        # it will return only the content (we can use more than page content but i will keep it simple for now
        return [chunk.page_content for chunk in text_chunks]

    except Exception as e:
        print(f"An error occurred: {e}")
        return []
