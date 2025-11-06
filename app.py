import chainlit as cl
from inference import answer_question
from typing import Optional
import chainlit as cl
import asyncio
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
            resp = answer_question(user_text, top_k=4, threshold=0.75)

    except Exception as e:
        
        await loader.remove()
        await cl.Message(content=f"Erreur interne : {e}").send()
        return

    await loader.remove()

    await cl.Message(content=resp.get("answer", "Désolé, pas de réponse.")).send()