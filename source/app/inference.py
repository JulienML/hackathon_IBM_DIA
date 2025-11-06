import mariadb
from mistralai import Mistral
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from API_db import QAEmbeddingDataset
from setup_RAG import get_text_embedding
from dotenv import load_dotenv
import os


def load_embs():
    db = mariadb.connect(
        user="root",
        password="rootroot",
        host="localhost",
        port=3307, # Adjusted port for MariaDB
        database="hackathon"
    )
    cursor = db.cursor()
    dataset = QAEmbeddingDataset([])
    dataset.load_from_db()
    chunks = [entry.chunk for entry in dataset.qa_emb_list]
    chunk_embeddings = np.array([list(entry.vector_data.values()) for entry in dataset.qa_emb_list])
    cursor.close()
    db.close()
    return chunks, chunk_embeddings


load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if MISTRAL_API_KEY is None:
    raise RuntimeError("MISTRAL_API_KEY non défini.")


client = Mistral(api_key=MISTRAL_API_KEY)

chunks, chunk_embeddings = load_embs()

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
        retrieved_chunks = ["""There is no relevant information in the provided context.
                    Here are the available email addresses. Redirect the user to the appropriate email based on their question:
                    - **ESILV academic services**: scolarite-esilv@devinci.fr
                    - **EMLV academic services**: scolarite-emlv@devinci.fr
                    - **IIM academic services**: scolarite-iim@devinci.fr
                    - **Student accounting (scholarships, CVEC, tuition fees, lost card, refunds, invoices, re-enrollment)**: compta_etudiante@devinci.fr
                    - **Work-study programs (alternance)**: alternance-esilv@devinci.fr
                    - **International matters**: remy.sart@devinci.fr
                    - **If none of the topics match the request**: provide the academic services email for the relevant school (if the school is not specified, provide all three).
                    """]

    return retrieved_chunks


def _build_prompt(question: str, retrieved_chunks: list):
    prompt = """You are an ai created by true GOAAATS (Lorrain, Julien...). You are created and owned by the school to help students to answer their questions on the School.
There are 3 schools in the De Vinci Institute: ESILV (engineering school), EMLV (business school) and IIM (digital school).
Alright, brainiac! 🎓 Let's tackle your question together.
I've got some context to work with—check it out below!
Answer only to school related questions.
---------------------
{retrieved_chunks}
---------------------
NEVER mention the above context as "the context" or "the document".
Now, using *only* this info (no cheating with outside knowledge!), here's how I'd answer your question:
**Query:** {question}

**Answer:**
[Insert your answer here—with a sprinkle of fun, a dash of humor, and a whole lot of clarity.]
(And hey, if I don't know the answer, I'll admit it—no ego here, just vibes.)
""".format(retrieved_chunks='\n\n'.join(retrieved_chunks), question=question)

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




