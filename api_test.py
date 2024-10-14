from openai import OpenAI

openai = OpenAI(
    api_key = "aner123!",
    base_url = "http://127.0.0.1/v1"
)
# response = openai.images.generate(
#     prompt="A sunset over a mountain range",
#     model="dalle3"
# )
# print(response.data[0].url)

message = []
while True:
  user = input("You: ")
  user_dict = {
    "role": "user",
    "content": user
  }
  message.append(user_dict)
  completion = openai.chat.completions.create(
    model="gpt-4-turbo",
    messages=message
  )

  ai_dict = {
    "role": "assistant",
    "content": completion.choices[0].message.content
  }
  message.append(ai_dict)
  print(f"AI: {completion.choices[0].message.content}")