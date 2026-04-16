import chromadb
from chromadb.utils import embedding_functions

# ---------------------------
# EMBEDDING FUNCTION
# ---------------------------
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# ---------------------------
# CHROMA CLIENT + COLLECTION
# ---------------------------
client = chromadb.Client()

collection = client.get_or_create_collection(
    name="phrases",
    embedding_function=embedding_function
)


# ---------------------------
# STORE PHRASES
# ---------------------------
def store_phrases(phrases: list):
    """
    Store generated phrases in vector DB.
    """
    for i, phrase in enumerate(phrases):
        collection.add(
            documents=[phrase["sentence"]],
            metadatas=[phrase],
            ids=[f"id_{i}_{phrase['sentence'][:10]}"]
        )


# ---------------------------
# RETRIEVE SIMILAR
# ---------------------------
def retrieve_similar(query: str, n_results: int = 3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results