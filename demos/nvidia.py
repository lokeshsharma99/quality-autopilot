from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)

completion = client.chat.completions.create(
  model="qwen/qwen3-coder-480b-a35b-instruct",
  messages=[{"role":"user","content":"Hello, how are you?"}],
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,
  stream=False
)

print(completion.choices[0].message)

