# XET AI
This repository includes the codebase for XET AI team and LuminaryAI discord bot which is owned by us. XET is built by students, for the students.

<hr>

Currently, XET AI has a functional, user-friendly dashboard, an AI playground, and an API so you can use the AI in your app. The API supports image generation and text generation. We also have a Discord bot, "LuminaryAI," which runs in the main thread, while the API runs in a separate thread. The project is built entirely with Python, using FastAPI for the API and discord.py for the bot.

<hr>

**Current image generation models:**
* Flux-dev
* Flux-schnell
* SDXL-Turbo

available sizes: `'1024x1024', '1024x576', '1024x768', '512x512', '576x1024', '786x1024'`.
Ratelimit: 100 requests per minute.

<hr>

**Current text generation models:**
* GPT-4
* GPT-4-Turbo
* GPT-3.5
* GPT-3.5-Turbo
* Llama-3
* Llama-3.1
* Gemma-2
* Mistral

Note: model names are case-sensitive in code, use `gpt-4`, not `GPT-4`. Plus, we use some system prompts for the models.
Ratelimit: 1 request per minute.

<hr>

## Folders:
* `bot_utilities`: includes bunch of files, the files basically includes a lots of functions. we have imported them to other files.
* `events`: includes some files with events for the discord bot.
* `images`: includes some images that are used in bot's messages.
* `prefix`: includes too many file with the codes of prefix commands.
* `slash`: includes too many file with the codes of slash commands.
* `unused`: includes files with some unused functions, currently we don't need them. but we may need them in the feature. Please do not delete without asking.

## Files in the root folder:
* `api_test`: a simple file for testing the API in ur local environment.
* `api.py`: contains the code for the API.
* `main.py`: startup file.