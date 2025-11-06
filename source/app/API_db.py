from flask import Flask, request, jsonify
import mariadb
import pandas as pd
from typing import Union, IO
import json

app = Flask(__name__)

db = mariadb.connect(
    user="root",
    password="rootroot",
    host="localhost",
    port=3307, # Adjusted port for MariaDB
    database="hackathon"
)
cursor = db.cursor()

class QAEntry:
    def __init__(self, question: str, response: str, subject: str):
        self.question = question
        self.response = response
        self.subject = subject

    def to_dict(self):
        """
        Convert the QAEntry to a dictionary.
        """
        return {"question": self.question, "response": self.response, "subject": self.subject}
    
    def insert_to_db(self):
        """
        Insert the QAEntry into the MySQL database.
        """
        sql = "INSERT INTO qa_table (question, response, subject) VALUES (%s, %s, %s)"
        val = (self.question, self.response, self.subject)
        cursor.execute(sql, val)
        db.commit()
    
    def update_in_db(self, id: int):
        """
        Update the QAEntry in the MySQL database by id.
        Args:
            id (int): The ID of the entry to update.
        """
        sql = "UPDATE qa_table SET question = %s, response = %s, subject = %s WHERE id = %s"
        val = (self.question, self.response, self.subject, id)
        cursor.execute(sql, val)
        db.commit()
class QADataset:
    def __init__(self, qa_list: list[QAEntry]):
        self.qa_list = qa_list
    
    @staticmethod
    def from_csv(file_or_path: Union[str, IO]):
        """
        Create a QADataset from a CSV file.
        Args:
            file_or_path (Union[str, IO]): Path to the CSV file or file-like object.
        """
        df = pd.read_csv(file_or_path)
        qa_list = [QAEntry(row['question'], row['response'], row['subject']) for _, row in df.iterrows()]
        return QADataset(qa_list)
    
    def insert_to_db(self):
        for qa in self.qa_list:
            qa.insert_to_db()

class QAEmbeddingEntry:
    def __init__(self, chunk: str, vector_data: dict):
        self.chunk = chunk
        self.vector_data = vector_data

    def to_dict(self):
        """
        Convert the QAEmbeddingEntry to a dictionary.
        """
        return {"chunk": self.chunk, "vector_data": self.vector_data}

    def insert_to_db(self, cursor, db):
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

    def update_in_db(self, id: int, cursor, db):
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

    def load_from_db(self):
        """
        Load all QAEmbeddingEntry objects from the MySQL database.
        Args:
            cursor: MySQL cursor object.
        """
        # MySQL Configuration
        db = mariadb.connect(
            user="root",
            password="rootroot",
            host="localhost",
            port=3307, # Adjusted port for MariaDB
            database="hackathon"
        )
        cursor = db.cursor()
        
        cursor.execute("SELECT chunk, vector_data FROM qa_embs")
        rows = cursor.fetchall()
        qa_emb_list = [
            QAEmbeddingEntry(chunk, json.loads(vector_data)) for (chunk, vector_data) in rows if vector_data
        ]
        self.qa_emb_list = qa_emb_list
        

    def insert_to_db(self, cursor, db):
        """
        Insert all QAEmbeddingEntry objects in the dataset into the MySQL database.
        Args:
            cursor: MySQL cursor object.
            db: MySQL connection object.
        """
        for qa_emb in self.qa_emb_list:
            qa_emb.insert_to_db(cursor, db)


# Create
@app.route('/qa', methods=['POST'])
def add_qa():
    data = request.json
    qa_entry = QAEntry(data['question'], data['response'], data['subject'])
    qa_entry.insert_to_db()
    return jsonify({"message": "Q&A added"}), 201

# Create from CSV
@app.route('/qa/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    dataset = QADataset.from_csv(file)
    dataset.insert_to_db()
    return jsonify({"message": "Q&A added from CSV"}), 201

# Read
@app.route('/qa', methods=['GET'])
def get_all_qa():
    cursor.execute("SELECT * FROM qa_table")
    qas = [QAEntry(question, response, subject).to_dict() for (id, question, response, subject) in cursor]
    return jsonify(qas)

# Read (Single)
@app.route('/qa/<int:id>', methods=['GET'])
def get_qa(id):
    cursor.execute("SELECT * FROM qa_table WHERE id = %s", (id,))
    qa = cursor.fetchone()
    if qa:
        return jsonify(QAEntry(qa[1], qa[2], qa[3]).to_dict())
    return jsonify({"message": "Not found"}), 404

# Update
@app.route('/qa/<int:id>', methods=['PUT'])
def update_qa(id):
    data = request.json
    new_qa_entry = QAEntry(data['question'], data['response'], data['subject'])
    new_qa_entry.update_in_db(id)
    return jsonify({"message": "Q&A updated"})

# Delete
@app.route('/qa/<int:id>', methods=['DELETE'])
def delete_qa(id):
    cursor.execute("DELETE FROM qa_table WHERE id = %s", (id,))
    db.commit()
    return jsonify({"message": "Q&A deleted"})

if __name__ == '__main__':
    app.run(debug=True)
    
    

