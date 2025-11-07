import numpy as np
import os
from dotenv import load_dotenv

from utils.mistralWrapper import MistralWrapper
from utils.mariaDBWrapper import MariaDBWrapper

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if MISTRAL_API_KEY is None:
    raise RuntimeError("MISTRAL_API_KEY non défini.")

mistral_wrapper = MistralWrapper(api_key=MISTRAL_API_KEY)
mariadb_wrapper = MariaDBWrapper(
    host="localhost",
    port=3307,  # Adjusted port for MariaDB
    user="root",
    password="rootroot",
    database="hackathon"
)

if __name__ == "__main__":
    with open('./data/data.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove empty lines and strip whitespace
    chunks = [line.strip() for line in lines if line.strip()]

    print(f"Total chunks after cleaning: {len(chunks)}")

    print(f"Calculating embeddings for {len(chunks)} chunks...")
    chunk_embeddings = np.array([mistral_wrapper.embed_text(chunk) for chunk in chunks])
    print(chunk_embeddings.shape)
    
    print("Uploading embeddings to database...")
    mariadb_wrapper.upload_embs_to_db(chunks, chunk_embeddings)
    print("Upload complete.")
