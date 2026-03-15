import os
import json
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from tqdm import tqdm
from src.config import BASE_DIR, DATA_DIR

# ChormaDB folder
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

def create_vector_db():

    file_path = os.path.join(DATA_DIR, "movies_dataset.json")
    if not os.path.exists(file_path):
        print("Error: Data dir not found")
        return
    
    with open(file_path, "r", encoding="utf-8") as f:
        movies = json.load(f)

    # Convert JSON into Langchain document object
    documents = []
    for movie in movies:
        # Exclude meta data from embedding
        meta = {
            "movie_id" : movie.get("movie_id"),
            "title" : movie.get("title"),
            "director" : movie.get("technical_details", {}).get("director", "Unknown"),
            "release_year" : movie.get("release_year") or 0,
            "poster_url" : movie.get("display_assets", {}).get("poster_url", "")
        }

        doc = Document(
            page_content=movie["content_payload_for_embedding"],
            metadata=meta
        )
        documents.append(doc)

    print(f"Preparing langchain documents: {len(documents)}")
    print("Processing text-embedding...")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-V2")

    batch_size = 50
    db = None

    for i in tqdm(range(0, len(documents), batch_size), desc="Building Vector Index"):
        batch = documents[i : i + batch_size]
        if db is None:
            db = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=CHROMA_PATH
            )
        else:
            db.add_documents(batch)

    print(f"Finishing!, vector data saved into: {CHROMA_PATH}")

if __name__ == "__main__":
    create_vector_db()