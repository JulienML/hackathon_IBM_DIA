import mariadb
from mariadb import Connection, Cursor
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class QAEmbeddingEntry:
    def __init__(self, chunk: str, vector_data: dict):
        self.chunk = chunk
        self.vector_data = vector_data

    def to_dict(self):
        """
        Convert the QAEmbeddingEntry to a dictionary.
        """
        return {"chunk": self.chunk, "vector_data": self.vector_data}

    def insert_to_db(self, db: Connection, cursor: Cursor):
        """
        Insert the QAEmbeddingEntry into the MySQL database.
        Args:
            cursor: MySQL cursor object.
            db: MySQL connection object.
        """
        sql = "INSERT INTO qa_embs (chunk, vector_data) VALUES (%s, %s)"
        val = (self.chunk, json.dumps(self.vector_data))
        cursor.execute(sql, val)
        db.commit()

    def update_in_db(self, id: int, db: Connection, cursor: Cursor):
        """
        Update the QAEmbeddingEntry in the MySQL database by id.
        Args:
            id (int): The ID of the entry to update.
            cursor: MySQL cursor object.
            db: MySQL connection object.
        """
        sql = "UPDATE qa_embs SET chunk = %s, vector_data = %s WHERE id = %s"
        val = (self.chunk, json.dumps(self.vector_data), id)
        cursor.execute(sql, val)
        db.commit()

class QAEmbeddingDataset:
    def __init__(self, qa_emb_list: list[QAEmbeddingEntry]):
        self.qa_emb_list = qa_emb_list

    def load_from_db(self, db: Connection, cursor: Cursor):
        """
        Load all QAEmbeddingEntry objects from the MySQL database.
        Args:
            cursor: MySQL cursor object.
        """
        cursor.execute("SELECT chunk, vector_data FROM qa_embs")
        rows = cursor.fetchall()
        qa_emb_list = [
            QAEmbeddingEntry(chunk, json.loads(vector_data)) for (chunk, vector_data) in rows if vector_data
        ]
        self.qa_emb_list = qa_emb_list

    def insert_to_db(self, db: Connection, cursor: Cursor):
        """
        Insert all QAEmbeddingEntry objects in the dataset into the MySQL database.
        Args:
            cursor: MySQL cursor object.
            db: MySQL connection object.
        """
        for qa_emb in self.qa_emb_list:
            qa_emb.insert_to_db(db, cursor)

class MariaDBWrapper:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.db = mariadb.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()
    
    def retrieve_chunks(self, question_embedding: np.ndarray, top_k: int = 4, threshold: float = 0.75) -> list[str]:
        # Load chunks and embeddings from the database
        dataset = QAEmbeddingDataset([])
        dataset.load_from_db(self.db, self.cursor)
        chunks = [entry.chunk for entry in dataset.qa_emb_list]
        chunk_embeddings = np.array([list(entry.vector_data.values()) for entry in dataset.qa_emb_list])

        # Calculate similarity scores
        similitudes = [
            {
                "document": chunk,
                "similarity": cosine_similarity(
                    question_embedding, emb.reshape(1, -1)
                )[0][0],
            }
            for chunk, emb in zip(chunks, chunk_embeddings)
        ]

        # Keep top_k most similar chunks above the threshold
        similitudes.sort(key=lambda x: x["similarity"], reverse=True)
        retrieved_chunks = similitudes[:top_k]

        retrieved_chunks = [item["document"] for item in retrieved_chunks if item["similarity"] >= threshold]

        # If no chunks meet the threshold, return default email addresses
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

        return retrieved_chunks
    
    def upload_embs_to_db(self, chunks: list[str], chunk_embeddings: np.ndarray):
        for chunk, embedding in zip(chunks, chunk_embeddings):
            vector_data = {str(i): float(embedding[i]) for i in range(len(embedding))}
            self.cursor.execute(
                "INSERT INTO qa_embs (chunk, vector_data) VALUES (?, ?)",
                (chunk, json.dumps(vector_data))
            )
        self.db.commit()