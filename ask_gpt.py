from g4f.client import Client

def ask_gpt(ask_text):

    print(ask_text)

    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": ask_text}]
    )
    return f'gpt: {response.choices[0].message.content}'