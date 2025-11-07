import chainlit as cl
from dotenv import load_dotenv
import os

from utils.mistralWrapper import MistralWrapper
from utils.mariaDBWrapper import MariaDBWrapper

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if MISTRAL_API_KEY is None:
    raise RuntimeError("MISTRAL_API_KEY non défini.")

mistral_wrapper = MistralWrapper(api_key=MISTRAL_API_KEY)

mariadb_wrapper = MariaDBWrapper(
    host="localhost",
    port=3307,  # Adjusted port for MariaDB
    user="root",
    password="rootroot",
    database="hackathon"
)

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin",
            metadata={"role": "admin", "provider": "credentials"}
        )
    return None

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Politique d'absence",
            message="Combien d'absences ai-je droit pendant l'année ?"
        ),

        cl.Starter(
            label="Contact Alternance",
            message="Qui dois-je contacter concernant mon contrat d'apprentissage ?"
        ),
        cl.Starter(
            label="Badge perdu",
            message="Que faire si j'ai perdu mon badge ?"
        ),
        cl.Starter(
            label="Informations boursiers",
            message="Comment bénéficier d'une bourse ?"
        )
    ]
    
@cl.on_message
async def main(message: str):
    user_text = message if isinstance(message, str) else message.content

    loader = await cl.Message(content="⏳ Je réfléchis...").send()

    try:
        question_embedding = mistral_wrapper.embed_text(user_text)
        retrieved_chunks = mariadb_wrapper.retrieve_chunks(question_embedding)

        resp = mistral_wrapper.answer_question(question=user_text, retrieved_chunks=retrieved_chunks)

    except Exception as e:
        
        await loader.remove()
        await cl.Message(content=f"Erreur interne : {e}").send()
        return

    await loader.remove()

    await cl.Message(content=resp.get("answer", "Désolé, pas de réponse.")).send()