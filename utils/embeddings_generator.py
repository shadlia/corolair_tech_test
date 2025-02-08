from openai import OpenAI
import os
from dotenv import load_dotenv
import lancedb


db = lancedb.connect("~/.lancedb-tabs")

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def create_embeddings(text_chunks):
    """
    Generates embeddings for a list of text chunks using OpenAI's text-embedding-3-small model.

    Parameters:
    text_chunks (list): A list of strings, where each string represents a chunk of text.

    Returns:
    list: A list of tuples, where each tuple contains the original text chunk and its corresponding embedding vector.
    """
    embeddings = []
    for chunk in text_chunks:
        response = (
            client.embeddings.create(
                input=[chunk],
                model="text-embedding-3-small",
            )
            .data[0]
            .embedding
        )

        embeddings.append((chunk, response))
    return embeddings


def store_embeddings(doc_id, embeddings):
    """
    Stores embeddings into a database after validating the format and creating the necessary table.

    Parameters:
    doc_id (str): The unique identifier for the document whose embeddings are being stored.
    embeddings (list): A list of tuples, where each tuple contains a text chunk and its corresponding embedding.

    Returns:
    None: The function inserts the embeddings into a database table, but does not return any value.
    It prints status messages indicating whether the table was created, if any errors occurred,
    and the number of records successfully inserted.

    Notes:
    - If the database table does not already exist, it will be created with the columns: "doc_id", "text", and "embedding".
    - The embeddings are inserted in batches to optimize database interaction.
    - If an item in the embeddings list does not match the expected format (tuple of two elements), an error message will be printed.
    """
    # Step 1: Try to create the table if it doesn't already exist
    table_name = "embeddings"
    try:
        db.create_table(table_name, ["doc_id", "text", "embedding"])
        print(f"Table '{table_name}' created.")
    except Exception as e:
        # If the table exists or there is any other error, log it
        print(f"Table '{table_name}' already exists or error: {e}")

    # Step 2: Initialize an empty list to store the records (dictionaries) to insert into the database
    records_to_insert = []

    # Loop through each item in the embeddings
    for item in embeddings:
        try:
            # Ensure the item is a tuple with exactly 2 elements (text and embedding)
            if isinstance(item, tuple) and len(item) == 2:
                text, embedding = (
                    item  # Unpack the tuple into text and embedding variables
                )
                # Create a dictionary with doc_id, text, and embedding, and append it to the records list
                record = {"doc_id": doc_id, "text": text, "embedding": embedding}
                records_to_insert.append(record)
            else:
                # If the item is not a tuple or has an incorrect number of elements, print an error message
                print(f"Invalid item format (expected tuple of 2 elements): {item}")
        except Exception as e:
            # Print an error message if there is an issue processing the chunk
            print(f"Error processing chunk: {item}\nError: {e}")

    # Step 3: Attempt to insert the list of records into the database
    try:
        # Open the table where the records will be inserted
        tbl = db.open_table(table_name)
        # Add the list of records to the table
        tbl.add(records_to_insert)

        # Step 4: Print how many records were successfully inserted
        print(f"Inserted {len(records_to_insert)} records into '{table_name}'.")
    except Exception as e:
        # If there's an error inserting records, print the error message
        print(f"Error inserting records into the database: {e}")


def get_query_embedding(query):
    """
    Generates an embedding vector for a given query using OpenAI's API.
    """
    try:
        response = client.embeddings.create(
            input=[query],
            model="text-embedding-3-small",
        )
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
