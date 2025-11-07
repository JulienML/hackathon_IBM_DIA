from mistralai import Mistral
import numpy as np

class MistralWrapper:
    def __init__(self, api_key: str, embedding_model: str = "mistral-embed", chat_model: str = "mistral-small-latest"):
        self.client = Mistral(api_key=api_key)
        self.embedding_model = embedding_model
        self.chat_model = chat_model

    def embed_text(self, text: str) -> np.ndarray:
        embeddings_batch_response = self.client.embeddings.create(
            model=self.embedding_model,
            inputs=text
        )

        return np.array([embeddings_batch_response.data[0].embedding])

    def _build_prompt(self, question: str, retrieved_chunks: list):
        prompt = """
        Context information is below.
        ---------------------
        {retrieved_chunks}
        ---------------------
        Given the context information and not prior knowledge, answer the query.
        Query: {question}
        Answer:
        """.format(retrieved_chunks='\n\n'.join(retrieved_chunks), question=question)

        return prompt

    def _call_mistral(self, prompt: str) -> str:
        messages = [
            {
                "role": "user", "content": prompt
            }
        ]
        chat_response = self.client.chat.complete(
            model=self.chat_model,
            messages=messages
        )

        return (chat_response.choices[0].message.content)

    def answer_question(self, question: str, retrieved_chunks: list[str]) -> dict:
        # Building a prompt and calling the LLM model
        prompt = self._build_prompt(question, retrieved_chunks)
        try:
            answer_text = self._call_mistral(prompt)
        except Exception as e:
            return {
                "answer": f"Désolé, une erreur est survenue lors de l'appel au modèle : {e}",
                "docs": retrieved_chunks,
            }

        return {"answer": answer_text, "docs": retrieved_chunks}