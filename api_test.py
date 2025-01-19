from openai import OpenAI

openai = OpenAI(
    api_key = "aner123!",
    base_url = "http://127.0.0.1:6705/v1"
)

response = openai.images.generate(
    prompt="A sunset over a mountain range",
    model="flux-dev",
    size="576x1024"
)
print(response)
print(response.data[0].url)