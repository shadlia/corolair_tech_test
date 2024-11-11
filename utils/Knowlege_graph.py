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
        node_id = f"{doc_id}_node_{idx}"
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


def retrieve_relevant_chunks_from_db(doc_id: str, query: str, top_k: int = 3):
    """
    Retrieve the most relevant document chunks from the database based on a query embedding.

    This function:
    - Retrieves all document nodes associated with a given `doc_id` from the LanceDB.
    - It filters and calculates the cosine similarity between the query embedding and each chunk's embedding.
    - It then returns the top K chunks with the highest similarity.

    Parameters:
    doc_id (str): The identifier for the document whose chunks to retrieve.
    query (str): The query string used to generate the query embedding.
    top_k (int): The number of top relevant chunks to return (default is 3).

    Returns:
    list: A list of relevant chunks, each containing a `node_id`, `text`, and `similarity`.
    """
    try:
        table_name = "document_graph_nodes"

        # Step 1: Open the table
        table = db.open_table(table_name)

        # Step 2: Filter rows based on doc_id
        all_data = table.to_pandas()  # Load the table into a DataFrame
        filtered_data = all_data[
            all_data["payload"].apply(lambda x: x["meta"]["doc_id"] == doc_id)
        ]

        # Check if any data is returned for the given doc_id
        if filtered_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No chunks found for document ID: {doc_id} or document doesn't exist",
            )

        # Step 3: Generate embedding for the query
        query_embedding = get_query_embedding(query)

        # Step 4: Calculate cosine similarity between query embedding and each chunk embedding
        filtered_data["similarity"] = filtered_data["vector"].apply(
            lambda x: cosine_similarity([query_embedding], [x])[0][0]
        )

        # Step 5: Sort by similarity and get the top_k results
        top_results_df = filtered_data.nlargest(top_k, "similarity")

        # Step 6: Format the results and ensure each chunk has valid text
        relevant_chunks = [
            {
                "node_id": row["id"],
                "text": (
                    row["payload"]["content"] if "content" in row["payload"] else ""
                ),
                "similarity": row["similarity"],
            }
            for _, row in top_results_df.iterrows()
        ]

        # Step 7 : Filter out any chunks where the content is empty
        relevant_chunks = [chunk for chunk in relevant_chunks if chunk["text"]]

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
