import chainlit as cl
from inference import answer_question
from typing import Optional
import chainlit as cl
from dotenv import load_dotenv

load_dotenv()


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin",
            metadata={"role": "admin", "provider": "credentials"}
        )
    return None
    

WELCOME_TEXT = """
Bonjour 👋 — je suis l'assistant étudiant.
Pose ta question (inscriptions, absences, international, alternance, ...).
Si tu as un doute, contacte directement les services officiels.
"""

# @cl.on_chat_start
# async def start():
#     # afficher logo si tu veux : ![](static/logo.png)
#     await cl.Message(content=WELCOME_TEXT).send()

@cl.on_message
async def main(message: str):
    user_text = message if isinstance(message, str) else message.content
    await cl.Message(content="⏳ Je réfléchis...").send()

    try:
        # Appel de la fonction RAG
        resp = answer_question(user_text, top_k=4, threshold=0.75)
    except Exception as e:
        await cl.Message(content=f"Erreur interne : {e}").send()
        return

    # Envoyer la réponse
    await cl.Message(content=resp.get("answer", "Désolé, pas de réponse.")).send()

