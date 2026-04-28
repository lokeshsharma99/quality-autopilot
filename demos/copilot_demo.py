from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:3030/v1", api_key="optional")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hi"}]
)
print(response.choices[0].message.content)
