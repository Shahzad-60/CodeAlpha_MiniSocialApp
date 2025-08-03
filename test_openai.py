import openai

openai.api_key = "sk23456hgfdsnbvcx nbvcxhgf"  # ← yahan apni API key daalo

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "What is Python?"},
    ]
)

print(response['choices'][0]['message']['content'])
