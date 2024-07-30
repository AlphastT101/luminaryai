# from openai import OpenAI

# openai = OpenAI(
#     api_key = "aner123!",
#     base_url = "http://127.0.0.1:6077/v1"
# )
# response = openai.images.generate(
#     prompt=input("You: "),
#     model="dalle3"
# )
# # print(response.error)
# print(response.data[0].url)


from openai import OpenAI
from os import getenv

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
  base_url="http://127.0.0.1:6077/v1",
  api_key="aner123!",
)

completion = client.chat.completions.create(
  model="blabla",
  messages=[
    {
      "role": "user",
      "content": "hi",
    },
  ],
)
print(completion)