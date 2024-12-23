from openai import OpenAI

openai = OpenAI(
    api_key = "hi, i love you.",
    base_url = "http://192.168.0.105:6750/v1"
)
response = openai.images.generate(
    prompt="A sunset over a mountain range",
    model="flux-dev",
    size="1024x1024"
)
print(response)
print(response.data[0].url)