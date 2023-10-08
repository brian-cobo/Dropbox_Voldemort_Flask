import openai
from chamber_of_secrets import get_secret


def get_chat_gpt_response(prompt, max_tokens=500):
    openai.api_key = get_secret('CHATGPT_API_SECRET')
    response = openai.Completion.create(
        engine="text-davinci-003",  # You can choose a different engine like "curie" if needed
        prompt=prompt,
        max_tokens=max_tokens
    )

    return response.choices[0].text.strip()
