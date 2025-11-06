from mistralai import Mistral
import numpy as np
import json
import time
from dotenv import load_dotenv
import os
import mariadb

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if MISTRAL_API_KEY is None:
    raise RuntimeError("MISTRAL_API_KEY non défini.")


client = Mistral(api_key=MISTRAL_API_KEY)

def get_text_embedding(input):
    embeddings_batch_response = client.embeddings.create(
        model="mistral-embed",
        inputs=input
    )
    #print(embeddings_batch_response)
    #time.sleep(0.2)  # to avoid rate limit
    return embeddings_batch_response.data[0].embedding


def upload_embs_to_db(chunks, chunk_embeddings):
    db = mariadb.connect(
            user="root",
            password="rootroot",
            host="localhost",
            port=3307, # Adjusted port for MariaDB
            database="hackathon"
        )
    cursor = db.cursor()
    for chunk, embedding in zip(chunks, chunk_embeddings):
        vector_data = {str(i): float(embedding[i]) for i in range(len(embedding))}
        cursor.execute(
            "INSERT INTO qa_embs (chunk, vector_data) VALUES (?, ?)",
            (chunk, json.dumps(vector_data))
        )
    db.commit()
    cursor.close()
    db.close()


if __name__ == "__main__":

    with open('./data/data.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Remove empty lines and strip whitespace
    chunks = [line.strip() for line in lines if line.strip()]

    print(f"Total chunks after cleaning: {len(chunks)}")
    print(f'max chunk length: {max(len(chunk) for chunk in chunks)}')

    # chunks = chunks[:20]  # limit to first 20 chunks for testing

    print(f"Calculating embeddings for {len(chunks)} chunks...")
    chunk_embeddings = np.array([get_text_embedding(chunk) for chunk in chunks])
    print(chunk_embeddings.shape)
    
    print("Uploading embeddings to database...")
    upload_embs_to_db(chunks, chunk_embeddings)
    print("Upload complete.")
