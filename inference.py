from getpass import getpass
from mistralai import Mistral
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from setup_RAG import get_text_embedding
from dotenv import load_dotenv
import os

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
CHUNKS_PATH = "chunks_with_embeddings.json"

if MISTRAL_API_KEY is None:
    raise RuntimeError("MISTRAL_API_KEY non défini.")


client = Mistral(api_key=MISTRAL_API_KEY)

with open("chunks_with_embeddings.json", "r", encoding="utf-8") as f:
    data = json.load(f)

chunks = [item["text"] for item in data]
chunk_embeddings = np.array([item["embedding"] for item in data])


def _retrieve(question:str, top_k: int = 4, threshold: float = 0.75):
    q_embeddings = np.array([get_text_embedding(question)])
    similitudes = [
        {
            "document": chunk,
            "similarity": cosine_similarity(
                q_embeddings, emb.reshape(1, -1)
            )[0][0],
        }
        for chunk, emb in zip(chunks, chunk_embeddings)
    ]

    similitudes.sort(key=lambda x: x["similarity"], reverse=True)
    retrieved_chunks = similitudes[:top_k]

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

    #print("Retrieved chunks: ", retrieved_chunks)
    #print("Number of retrieved chunks: ", len(retrieved_chunks))
    #print('similarity scores of retrieved chunks: ', [item["similarity"] for item in similitudes[:top_k]])
    #len(retrieved_chunks)

    return retrieved_chunks


def _build_prompt(question: str, retrieved_chunks: list):
    prompt = """
    Context information is below.
    ---------------------
    {retrieved_chunks}
    ---------------------
    Given the context information and not prior knowledge, answer the query.
    Query: {question}
    Answer:
    """.format(retrieved_chunks='\n\n'.join(retrieved_chunks), question=question)

    #print(prompt)
    return prompt



def _call_mistral(client, user_message, model="mistral-small-latest"):
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


def answer_question(question: str, top_k: int = 4, threshold: float = 0.75):
    # Retrieving the relevant documents or the email addresses if no result
    retrieved_docs = _retrieve(question, top_k=top_k, threshold=threshold)

    # Building a prompt and calling the LLM model
    prompt = _build_prompt(question, retrieved_docs)
    try:
        answer_text = _call_mistral(client, prompt)
    except Exception as e:
        return {
            "answer": f"Désolé, une erreur est survenue lors de l'appel au modèle : {e}",
            "docs": retrieved_docs,
        }

    return {"answer": answer_text, "docs": retrieved_docs}




