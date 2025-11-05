

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from hackathon_IBM_DIA.setup_RAG import get_text_embedding


def embed_query():
    pass


def retrieve_documents():
    pass


def build_prompt():
    prompt = f""


def generate_answer():
    pass


def rag_inference():
    pass





if __name__ == "__main__":
    user_question = input("Pose ta question: ")
    question_embeddings = np.array([get_text_embedding(user_question)])

    print(question_embeddings.shape)

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




