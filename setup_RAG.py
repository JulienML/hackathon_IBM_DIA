from mistralai import Mistral
import numpy as np
from getpass import getpass
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
CHUNKS_PATH = "chunks_with_embeddings.json"

if MISTRAL_API_KEY is None:
    raise RuntimeError("MISTRAL_API_KEY non défini.")


client = Mistral(api_key=MISTRAL_API_KEY)

def get_text_embedding(input):
    embeddings_batch_response = client.embeddings.create(
        model="mistral-embed",
        inputs=input
    )
    print(embeddings_batch_response)
    time.sleep(0.2)  # to avoid rate limit
    return embeddings_batch_response.data[0].embedding


if __name__ == "__main__":
    
    with open('data.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove empty lines and strip whitespace
    chunks = [line.strip() for line in lines if line.strip()]

    print(f"Total chunks after cleaning: {len(chunks)}")
    print(f'max chunk length: {max(len(chunk) for chunk in chunks)}')

    # chunks = chunks[:20]  # limit to first 20 chunks for testing

    print(f"Calculating embeddings for {len(chunks)} chunks...")
    chunk_embeddings = np.array([get_text_embedding(chunk) for chunk in chunks])
    print(chunk_embeddings.shape)

    data = [
        {"text": chunk, "embedding": emb.tolist() if hasattr(emb, "tolist") else list(emb)}
        for chunk, emb in zip(chunks, chunk_embeddings)
    ]

    with open("chunks_with_embeddings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(data)} chunks with embeddings to chunks_with_embeddings.json")
