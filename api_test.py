from openai import OpenAI

client = OpenAI(
    api_key = "aner123!",
    base_url = "http://127.0.0.1:6077/v1"
)
# response = client.images.generate(
#     prompt=input("You: "),
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
  completion = client.chat.completions.create(
    model="gpt-4o",
    messages=message
  )

  ai_dict = {
    "role": "assistant",
    "content": completion.response
  }
  message.append(ai_dict)
  print(f"AI: {completion.response}")

  print(message)