CREATE DATABASE hackathon;
USE hackathon;
CREATE TABLE IF NOT EXISTS qa_embs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    chunk TEXT NOT NULL,
    vector_data JSON NOT NULL
);

CREATE TABLE qa_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    subject VARCHAR(255) NOT NULL
);
