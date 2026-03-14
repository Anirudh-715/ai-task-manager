import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_mood(text):

    prompt = f"""
    Analyze the user's emotional state.

    Return ONLY this format:

    mood: <one word>
    energy: <number 1-10>

    Do NOT include explanations.

    User message: {text}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content.strip()

    return result

def ai_chat(messages):

    system_prompt = """
You are an AI productivity assistant.

Help the user with:
- productivity advice
- study plans
- focus techniques
- task planning

If the user asks for tasks, respond with a list like this:

- task 1
- task 2
- task 3

Keep answers concise and helpful.
"""

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=full_messages
    )

    return response.choices[0].message.content