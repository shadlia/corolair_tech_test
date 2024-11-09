# **Graph-Based Knowledge Retrieval API**

This is my attempt to solve the technical test for Corolair. I have implemented a RESTful API for knowledge retrieval and question answering on course materials, using a graph-based RAG (retrieval-augmented generation) method on PDF documents. This API leverages GraphRAG for complex knowledge linking, document embeddings for efficient retrieval, and OpenAI models for answer generation.

## Table of Contents

1. [Objective](#objective)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [API Overview](#api-overview)
6. [Endpoints](#endpoints)
7. [Usage Examples](#usage-examples)
8. [Testing & Documentation](#testing-and-documentation)
9. [Security Considerations](#security-considerations)
10. [Bonus : Agent Workflow ](#security-considerations)
11. [Notes and Future Enhancements](#Notes-and-Future-Enhancements)

---

## Objective

The API allows users to upload PDFs, create a knowledge graph, and retrieve information or direct answers based on content. Using GraphRAG enhances context understanding in question answering by creating an interconnected knowledge graph from course materials.

## Prerequisites

- **Python 3.8+**
- **API Keys**:
  - OpenAI API for LLM responses and embeddings
- **Libraries/Tools**:
  - LanceDB, Langchain(i had issues with Docling to handle Pdfs so i used langchain loader), FastAPI ....
  - Swagger for API documentation

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/shadlia/corolair_tech_test
   cd shadlia/corolair_tech_test
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   - Set up your OpenAI API key:
     ```bash
     export OPENAI_API_KEY='your_openai_api_key'
     ```
4. **Start your app**:
   ```bash
    uvicorn app:app --host 0.0.0.0 --port 8000
   ```

## Project Structure

The project is organized as follows:

```
├── app.py                 # Main application file
├── routes/                # Directory for route handlers
│   ├── answer.py          # Route for answering queries
│   ├── retrieve.py        # Route for retrieving content
│   └── upload.py          # Route for uploading PDFs
├── services/              # Directory for service logic
│   ├── answer_generator.py # Service for generating answers
│   ├── embeddings.py      # Service for handling embeddings
│   ├── graph.py           # Service for knowledge graph management
│   └── pdf_processor.py   # Service for processing PDFs
└── README.md              # Documentation for the API
```

## API Overview

The API provides knowledge retrieval and answering services by processing and embedding PDF documents, creating a knowledge graph, and allowing retrieval and answering through queries. The service is designed with three primary endpoints:

- **`/upload`**: Upload and process a PDF from a URL.
- **`/retrieve`**: Retrieve text chunks relevant to a query.
- **`/answer`**: Provide a direct answer based on the document content and the relevant chunks.

## Endpoints

### 1. **Upload Document** - `POST /upload`

- **Description**: Uploads a PDF from a given URL, processes it, and stores the resulting data for querying.
- **Parameters**:
  - `url` (string): URL to the PDF document.
- **Response**:
  - `document_id` (string): Unique identifier for the uploaded document.

### 2. **Retrieve Content** - `POST /retrieve`

- **Description**: Accepts a document ID and a query, returning relevant text chunks based on similarity scoring and the knowledge graph.
- **Parameters**:
  - `document_id` (string): The ID of the document to query.
  - `query` (string): The user's query.
- **Response**:
  - `results` (array): Array of text chunks with similarity scores.

### 3. **Answer Query** - `POST /answer`

- **Description**: Accepts a document ID and a query, returning a contextual answer if available.
- **Parameters**:
  - `document_id` (string): The ID of the document to query.
  - `query` (string): The user’s question.
- **Response**:
  - `answer` (string): Answer to the query, contextualized for learning.
  - `note` (string): Returns a note if an answer is not available in the document.

## Usage Examples

```bash
# Upload a document
curl -X POST -H "Content-Type: application/json" -d '{"url":"<pdf_url>"}' http://localhost:8000/upload
```

![Screenshot from 2024-11-09 16-10-13](https://github.com/user-attachments/assets/72a198cc-03d4-459c-a7a4-19aaab2ea777)

```bash
# Retrieve information
curl -X POST -H "Content-Type: application/json" -d '{"document_id": "doc_id", "query": "What is GraphRAG?"}' http://localhost:8000/retrieve
```

![Screenshot from 2024-11-09 16-11-21](https://github.com/user-attachments/assets/6aa2d51e-48b5-43e0-b652-a0c4050e0e76)

```bash
# Get a direct answer
curl -X POST -H "Content-Type: application/json" -d '{"document_id": "doc_id", "query": "Explain GraphRAG in simple terms."}' http://localhost:8000/answer
```

![Screenshot from 2024-11-09 16-11-49](https://github.com/user-attachments/assets/39c11958-de5c-490b-b046-f6b1149b887b)

Example of irrelevant query :
![Screenshot from 2024-11-09 16-12-47](https://github.com/user-attachments/assets/caed4c79-8b5a-4db7-b485-f6dbf9b4b5c7)

## Testing and Documentation

1. **Testing with Sample Data**:
   - Use [CBV Institute Level I Course Notes (PDF)](https://cbvinstitute.com/wp-content/uploads/2019/12/Level-I-Course-Notes-ENG.pdf) as test data.
2. **Swagger API Documentation**:
   - Access Swagger at `http://localhost:8000/docs` to view interactive documentation and test endpoints directly.
     ![Screenshot from 2024-11-09 16-16-47](https://github.com/user-attachments/assets/255e79f2-f5b3-4971-a3ff-0b74850611f5)

## Security Considerations

- **OpenAI Key Management**: Ensure OpenAI keys are stored securely and not hardcoded in the source.

## Bonus: Agent Workflow

### Workflow for Query Resolution:

1. **Chunk-Based Retrieval**:

   - The first step is to check the relevant chunks for the user query. Using document embeddings and similarity scoring, we retrieve the most relevant chunks from the document.

2. **LLM Response Generation**:

   - Once relevant chunks are retrieved, the system feeds these into an LLM (e.g., OpenAI) to generate a relevant answer.

3. **Answer Relevance Check**:

   - If the generated answer is deemed relevant, it is returned to the user.

4. **Fallback to Agent**:
   - If the answer is not relevant or the content is missing in the document, the fallback agent is invoked. This agent will provide alternative sources or generate a new answer based on external knowledge sources.

### Agent Workflow Diagram:

```plaintext
[User Query] --> [Check Chunks for Relevance]
       |
       v
[Relevant Chunks Found?] --- No --> [Invoke Agent for Alternative Answer]
       |
       v
    Yes
       |
       v
[LLM Generates Answer]
       |
       v
[Answer Relevant?] --- No --> [Invoke Agent for Alternative Answer]
       |
       v
    Yes
       |
       v
[Return Answer to User]
```

This workflow ensures the API can provide accurate answers based on the content of the uploaded documents, while also providing alternative solutions when necessary.

Example if the document doesnt provide an answer :
1- The agent start :
![Screenshot from 2024-11-09 17-05-49](https://github.com/user-attachments/assets/bb172533-81e4-43ce-85dd-6a9ee7d1784b)
2- VOILA we get the answer :
![Screenshot from 2024-11-09 17-16-38](https://github.com/user-attachments/assets/ad464867-e44d-4d46-95b2-3e64c6623f4a)

## Notes and Future Enhancements

Here are a few improvements i thought about to enhance the system:

- **Improved Similarity Calculation**: Explore advanced methods for calculating similarity between embeddings to better match relevant content or use langchain/llama_index functionalities
- **Enhanced Knowledge Graph Construction**: Use LanceDB's advanced capabilities for efficient knowledge graph storage and retrieval.
- **Integration with Docling**: I couldn't use Docling due to packages incompability with Langchain (used it for the agent and as pdf loader)
