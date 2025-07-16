## XET AI API

* **Base URL**: https://api.xet.one/v1
* **Playground:** https://play.xet.one
* **Site:** https://xet.one
<br><br>
-  **API key**:  [Dashboard](https://xet.one/dashboard) > API Tokens
- **Image Ratelimits**: 5 requests per minute.
- **Text Ratelimits**: 5 requests per minute.

### Image generation models
- `sdxl-turbo`, `flux`, `kontext`.
- available sizes: `'1024x1024', '1024x576', '1024x768', '512x512', '576x1024', '768x1024'`

### Text generation models[DISABLED]
- View at [/models](https://api.xet.one/v1/models)
- This list DOES NOT include image generation models, only text.

**Python3 code example for image generation:**
```python
from openai import OpenAI

openai = OpenAI(
    api_key = "API key here",
    base_url = "https://api.xet.one/v1"
)
response = openai.images.generate(
    prompt="A sunset over a mountain range",
    model="flux",
    size="1024x1024"
)
print(response.data[0].url)
```

**Python3 code example for text generation:**
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
    model="your model here",
    messages=message
  )

  ai_dict = {
    "role": "assistant",
    "content": completion.choices[0].message.content
  }
  message.append(ai_dict)
  print(f"AI: {completion.choices[0].message.content}")
```
