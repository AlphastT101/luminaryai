<h1 align="center">
  <img src="https://cdn.discordapp.com/attachments/1201176761422061678/1333426938626314240/logo.png?ex=6798da1c&is=6797889c&hm=63ddfbf2a12f60dc331a1fb0138f4aef6a2afea2d883f006bf67d4f345b4bfb0&" alt="icon" width="100"><br>
  XET AI
</h1>

This repository includes the codebase for XET AI team and LuminaryAI discord bot which is owned by us. XET is built by students, for the students.


Currently, XET AI has a functional, user-friendly dashboard, an AI playground, and an API so you can use the AI in your app. The API supports image generation and text generation. We also have a Discord bot, "LuminaryAI," which runs in the main thread, while the API runs in a separate thread. The project is built entirely with Python, using FastAPI for the API and discord.py for the bot.

<hr>

**🖼️ Current image generation models:**
* Flux-dev
* Flux-schnell
* SDXL-Turbo
* Poli

available sizes: `'1024x1024', '1024x576', '1024x768', '512x512', '576x1024', '786x1024'`.<br>
Ratelimit: 100 requests per minute.

**🔠 Current text generation models:**
* GPT-4
* GPT-4-Turbo
* GPT-3.5
* GPT-3.5-Turbo
* Llama-3
* Llama-3.1
* Gemma-2
* Mistral

Ratelimit: 1 request per minute.

> [!NOTE]  
> Model names are case-sensitive in code, use `gpt-4`, not `GPT-4`. Plus, we use some system prompts for the models.


<hr>

## 📁 Folders:
* `bot_utilities`: includes bunch of files, the files basically includes a lots of functions. we have imported them to other files.
* `events`: includes some files with events for the discord bot.
* `images`: includes some images that are used in bot's messages.
* `prefix`: includes too many file with the codes of prefix commands.
* `slash`: includes too many file with the codes of slash commands.
* `unused`: includes files with some unused functions, currently we don't need them. but we may need them in the feature. Please do not delete without asking.

## 🗃️ Files in the root folder:
* `api_test`: a simple file for testing the API in ur local environment.
* `api.py`: contains the code for the API.
* `main.py`: startup file.

<hr>

# 📄 API Docs

The models listed above is the only supported models and image sizes. Our API is in OpenAI format. Please join our [Discord](https://discord.com/invite/hmMBe8YyJ4) for more info.

* Python 3 code example for text generation:
```python
from openai import OpenAI

client = OpenAI(
  base_url="https://api.xet.one/v1",
  api_key="API key here",
)

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
```

* Python3 code example for image generation
```python
from openai import OpenAI

openai = OpenAI(
    api_key = "API key here",
    base_url = "https://api.xet.one/v1"
)
response = openai.images.generate(
    prompt="A sunset over a mountain range",
    model="flux-dev",
    size="1024x1024"
)
print(response.data[0].url)
```

<hr>

# 🔗 Links & other

* Website: https://xet.one
* Playground: https://play.xet.one
* Discord Server: https://discord.com/invite/hmMBe8YyJ4
* Email: xet@xet.one
* Support Email: support@xet.one