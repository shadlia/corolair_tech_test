from datetime import datetime
import lancedb
from lancedb.pydantic import LanceModel, Vector
import numpy as np
from pydantic import BaseModel
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from utils.embeddings_generator import get_query_embedding
from fastapi import HTTPException
from sklearn.metrics.pairwise import cosine_similarity

db = lancedb.connect("~/.lancedb")


# Define Metadata and Document schemas
class Metadata(BaseModel):
    doc_id: str
    source: str
    timestamp: datetime


class Document(BaseModel):
    content: str
    meta: Metadata


class LanceSchema(LanceModel):
    id: str
    vector: Vector(1536)
    payload: Document


def build_graph_and_store(doc_id, chunks):
    """
    Build a graph based on cosine similarity of embeddings and store nodes as documents in LanceDB.

    This function:
    - Creates a graph structure where nodes represent chunks of text.
    - Each node is associated with a document ID, text, and an embedding.
    - The function stores this data in a LanceDB table as documents with metadata.
    - The graph is built by calculating cosine similarity between the embeddings of each pair of chunks and adding edges if the similarity exceeds a threshold.
    - The table containing nodes and edges is created or updated in the LanceDB.

    Parameters:
    doc_id (str): The identifier for the document.
    chunks (list): A list of tuples containing text chunks and their corresponding embeddings.

    Returns:
    graph (networkx.Graph): A graph representing the document with nodes and edges based on cosine similarity.
    """
    # Step 1 : Initialize the graph
    graph = nx.Graph()

    # Step 2 : Prepare data for LanceDB
    data = []
    for idx, (text, embedding) in enumerate(chunks):
        timestamp = datetime.now()
        node_id = f"{doc_id}_node_{idx}_{timestamp}"

        timestamp = datetime.now()
        graph.add_node(idx, doc_id=doc_id, text=text, embedding=embedding)

        # Create LanceDB-compatible data entries
        document_entry = LanceSchema(
            id=node_id,
            vector=np.array(embedding),
            payload=Document(
                content=text,
                meta=Metadata(
                    doc_id=doc_id, source="source_example", timestamp=timestamp
                ),
            ),
        )
        data.append(document_entry)

    # Step 3 : Create table in LanceDB if not exists and add data
    table_name = "document_graph_nodes"
    if table_name not in db.table_names():
        tbl = db.create_table(table_name, data=data)
    else:
        tbl = db.open_table(table_name)
        tbl.add(data)
        print("Table after inserting new document:")
        print(tbl.to_pandas().to_string())  # Ensure it actually exists

    # Step 4 : Add edges based on cosine similarity of embeddings
    for i in range(len(chunks)):
        for j in range(i + 1, len(chunks)):
            embedding_i = np.array(chunks[i][1]).reshape(1, -1)
            embedding_j = np.array(chunks[j][1]).reshape(1, -1)
            similarity = cosine_similarity(embedding_i, embedding_j)[0][0]

            if (
                similarity > 0.7
            ):  # Adjust the threshold as needed : only add relation if similarity is greater than 0.7 (70% similarity)
                graph.add_edge(i, j, weight=similarity)

    return graph


from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def retrieve_relevant_chunks_from_db(doc_id: str, query: str, top_k: int = 3):
    """
    Retrieve the most relevant document chunks from the database based on a query embedding,
    manually calculating the cosine similarity between the query and each chunk.
    """
    try:
        table_name = "document_graph_nodes"
        table = db.open_table(table_name)

        # Step 1: Generate embedding for the query
        query_embedding = get_query_embedding(query)

        # Step 2: Retrieve document chunks
        results = (
            table.search(query_embedding)
            .where(f"payload['meta']['doc_id'] = '{doc_id}'")  # Filter by doc_id
            .limit(top_k * 2)  # Fetch extra results to filter empty content
            .to_list()
        )

        # Step 3: Calculate cosine similarity for each result and store it
        relevant_chunks = []
        for row in results:
            content = (
                row["payload"].get("content", "").strip()
            )  # Get content if available
            if content:
                # Retrieve the embedding for the current chunk
                chunk_embedding = np.array(row["vector"])

                # Calculate cosine similarity
                similarity = cosine_similarity([query_embedding], [chunk_embedding])[0][
                    0
                ]

                relevant_chunks.append(
                    {
                        "node_id": row["id"],
                        "text": content,
                        "similarity": similarity,  # Store similarity
                    }
                )

        # Step 4: Sort the results by similarity in descending order
        relevant_chunks.sort(key=lambda x: x["similarity"], reverse=True)

        # Limit the number of top_k results
        relevant_chunks = relevant_chunks[:top_k]

        # Step 5: Handle case if no relevant chunks were found
        if not relevant_chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No valid chunks found for document ID: {doc_id}",
            )

        return relevant_chunks

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving relevant chunks: {str(e)}"
        )
