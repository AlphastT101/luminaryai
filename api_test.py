from openai import OpenAI

openai = OpenAI(
    api_key = "aner123!",
    base_url = "https://stable.serveo.net/v1"
)
response = openai.images.generate(
    prompt=input("You: "),
    model="lumage-1"
)
print(response.data[0].url)