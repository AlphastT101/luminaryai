from openai import OpenAI

client = OpenAI(
    api_key = "api key",
    base_url = "http://45.139.50.97:6077/v1"
)

message = []
while True:
  user = input("You: ")
  user_dict = {
    "role": "user",
    "content": user
  }
  message.append(user_dict)
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=message
  )

  ai_dict = {
    "role": "assistant",
    "content": completion.response
  }
  message.append(ai_dict)
  print(f"AI: {completion.response}")





# response = client.images.generate(
#     prompt=input("You: "),
#     model="sdxl-turbo"
# )

# print(response.data[0].url)