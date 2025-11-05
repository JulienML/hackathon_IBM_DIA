from mistralai import Mistral
import requests
import numpy as np
import faiss
import os
from getpass import getpass

api_key= getpass("Type your API Key")
client = Mistral(api_key=api_key)

# chunk_size = 2048
# chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
# len(chunks)

with open('data.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove empty lines and strip whitespace
chunks = [line.strip() for line in lines if line.strip()]

print(f"Total chunks after cleaning: {len(chunks)}")
print(f'max chunk length: {max(len(chunk) for chunk in chunks)}')

import time

chunks = chunks[:20]  # limit to first 20 chunks for testing

def get_text_embedding(input):
    embeddings_batch_response = client.embeddings.create(
          model="mistral-embed",
          inputs=input
      )
    print(embeddings_batch_response)
    time.sleep(0.2)  # to avoid rate limit
    return embeddings_batch_response.data[0].embedding

print(f"Calculating embeddings for {len(chunks)} chunks...")
chunk_embeddings = np.array([get_text_embedding(chunk) for chunk in chunks])
print(chunk_embeddings.shape)

question = input("Quelle est ta question ? ")
question_embeddings = np.array([get_text_embedding(question)])

print(question_embeddings.shape)

from sklearn.metrics.pairwise import cosine_similarity

n = 4  # number of nearest neighbors to retrieve
threshold = 0.75  # similarity threshold

similitudes = [
    {
        "document": chunk,
        "similarity": cosine_similarity(
            question_embeddings, emb.reshape(1, -1)
        )[0][0],
    }
    for chunk, emb in zip(chunks, chunk_embeddings)
]

similitudes.sort(key=lambda x: x["similarity"], reverse=True)
retrieved_chunks = similitudes[:n]

retrieved_chunks = [item["document"] for item in retrieved_chunks if item["similarity"] >= threshold]

if not retrieved_chunks:
    retrieved_chunks = ["""Il n'y a pas d'informations pertinentes dans le contexte fourni. 
                        Voici les adresses mails disponibles. Redirige l'utilisateur vers la bonne adresse mail en fonction de sa question.
                        - service scolarité de l'ESILV : scolarite-esilv@devinci.fr
                        - service scolarité de l'EMLV: scolarite-emlv@devinci.fr
                        - service scolarité de l'IIM: scolarite-iim@devinci.fr
                        - comptabilité étudiante (Bourse, CVEC, frais de scolarité, perte carte, remboursement, facture, réinscription): compta_etudiante@devinci.fr
                        - alternance: alternance-esilv@devinci.fr
                        - international: remy.sart@devinci.fr
                        - si aucun des sujets ne correspond à la requête : donne l'addresse de la scolarité de l'école concernée (si l'école n'est pas précisée, donne les 3)
                        """]

print("Retrieved chunks: ", retrieved_chunks)
print("Number of retrieved chunks: ", len(retrieved_chunks))
print('similarity scores of retrieved chunks: ', [item["similarity"] for item in similitudes[:n]])
len(retrieved_chunks)

prompt = """
Context information is below.
---------------------
{retrieved_chunks}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {question}
Answer:
""".format(retrieved_chunks='\n\n'.join(retrieved_chunks), question=question)

print(prompt)

def run_mistral(user_message, model="mistral-small-latest"):
    messages = [
        {
            "role": "user", "content": user_message
        }
    ]
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )
    return (chat_response.choices[0].message.content)

run_mistral(prompt)

