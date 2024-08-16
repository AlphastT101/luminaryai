import io
import cv2
import yaml
import random
import discord
import asyncio
import aiohttp
import requests
import imagehash
import numpy as np
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from openai import AsyncOpenAI
from urllib.parse import quote
from bot_utilities.start_util import *
from bot_utilities.prompt_sys import prompt
from pymongo.mongo_client import MongoClient


with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)

mongodb = config["bot"]["mongodb"]
client = MongoClient(mongodb)
bot_token, api_key = start(client)
GPT_MODEL = config["bot"]["text_model"]
request_queue = asyncio.Queue()

openai_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


async def generate_response_cmd(ctx, user_input, history=[]):

    system_message = {
        "role": "system",
        "name": "LuminaryAI",
        "content": prompt,
    }

    member_info = {
        "id": str(ctx.author.id),
        "name": str(ctx.author),
    }

    user_message = {"role": "user", "name": member_info["name"], "content": user_input}
    history.append(user_message)

    messages = [system_message, *history]
    response = await openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages
    )

    generated_message = response.choices[0].message.content
    bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}
    history.append(bot_message)

    return generated_message, history

async def generate_response_slash(interaction, user_input, history=[]):

    system_message = {
        "role": "system",
        "name": "LuminaryAI",
        "content": prompt,
    }

    member_info = {
        "id": str(interaction.user.id),
        "name": str(interaction.user),
    }

    user_message = {"role": "user", "name": member_info["name"], "content": user_input}
    history.append(user_message)

    messages = [system_message, *history]
    response = await openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages
    )

    generated_message = response.choices[0].message.content
    bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}
    history.append(bot_message)

    return generated_message, history

async def generate_response_msg(message, user_input, history=[]):
    system_message = {
        "role": "system",
        "name": "LuminaryAI",
        "content": prompt,
    }
    member_info = {
        "id": str(message.author.id),
        "name": str(message.author),
    }
    user_message = {"role": "user", "name": member_info["id"], "content": user_input}
    history.append(user_message)
    messages = [system_message, *history]
    await request_queue.put((messages, history))

    response = await openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages
    )
    generated_message = response.choices[0].message.content
    bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}

    history.append(bot_message)
    return generated_message, history


async def process_queue():
    while True:
        messages, history = await request_queue.get()
        response = await openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages
        )
        generated_message = response.choices[0].message.content
        bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}
        history.append(bot_message)
        request_queue.task_done()



async def poly_image_gen(session, prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    async with session.get(image_url) as response:
        image_data = await response.read()
        return io.BytesIO(image_data)


    

async def generate_image_prodia(prompt, model, sampler, seed):
    async def create_job(prompt, model, sampler, seed):
        negative = "DO NOT INCLUDE NSFW OR ANYTHING AGE RESTRICTED. NO PORN"
        url = 'https://api.prodia.com/generate'
        params = {
            'new': 'true',
            'prompt': f'{quote(prompt)}',
            'model': model,
            'negative_prompt': f"{negative}",
            'steps': '100',
            'cfg': '9.5',
            'seed': f'{seed}',
            'sampler': sampler,
            'upscale': 'True',
            'aspect_ratio': 'square'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return data['job']
            
    job_id = await create_job(prompt, model, sampler, seed)
    url = f'https://api.prodia.com/job/{job_id}'
    headers = {
        'authority': 'api.prodia.com',
        'accept': '*/*',
    }

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers) as response:
                json = await response.json()
                if json['status'] == 'succeeded':
                    async with session.get(f'https://images.prodia.xyz/{job_id}.png?download=1', headers=headers) as response:
                        content = await response.content.read()
                        img_file_obj = io.BytesIO(content)
                        return img_file_obj
    

def web_search(query):
    # DuckDuckGo Instant Answers API endpoint
    api_url = 'https://api.duckduckgo.com/'

    # Parameters for the search query
    params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1
    }

    try:
        # Make the API request
        response = requests.get(api_url, params=params)
        data = response.json()

        # Check if there are relevant results
        if 'AbstractText' in data:
            result = data['AbstractText']
        elif 'Definition' in data:
            result = data['Definition']
        else:
            result = None

        return result

    except requests.RequestException as e:
        return f"An error occurred: {e}"
    


def search_image(query):
    search_url = f"https://www.bing.com/images/search?q={query}"
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all image tags
        image_tags = soup.find_all('img', {'class': 'mimg'})
        image_urls = [img['src'] for img in image_tags[:10]]
        
        return image_urls
    except requests.exceptions.RequestException as e:
        print(f"Error searching for images: {e}")
        return None



async def create_and_send_embed(query, client, interaction, image_urls, target_size=(256, 256)):
    channel = client.get_channel(interaction.channel.id)

    try: message = await channel.fetch_message(interaction.message.id)
    except AttributeError: message = None

    # Helper function to check for duplicates
    def is_duplicate(img_hash, img_cv):
        for buffer in buffers:
            similarity = cv2.matchTemplate(buffer, img_cv, cv2.TM_CCOEFF_NORMED)
            if np.max(similarity) > 0.15:
                return True
        return False

    images = []
    hashes = set()
    buffers = []

    async with aiohttp.ClientSession() as session:
        for url in image_urls:
            try:
                async with session.get(url) as response:
                    # Get the content type from the response headers
                    content_type = response.headers.get('Content-Type')
                    if content_type and 'image' in content_type:
                        img_data = await response.read()
                        
                        # Special handling for GIFs
                        if 'gif' in content_type:
                            images.append((img_data, 'gif'))
                            continue

                        img = Image.open(BytesIO(img_data))
                        img = img.resize(target_size, Image.LANCZOS)

                        # Convert image to numpy array for OpenCV
                        img_cv = np.array(img)
                        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)

                        # Calculate image hash
                        img_hash = imagehash.average_hash(img)

                        # Check for duplicates
                        if is_duplicate(img_hash, img_cv):
                            continue

                        # Add image and buffer if not duplicate
                        hashes.add(img_hash)
                        images.append((img_data, 'image'))
                        buffers.append(img_cv)
                    else:
                        # If the content is not an image, skip it
                        continue

            except Exception as e:
                continue

    if not images:
        await channel.send("No valid images found.")
        return

    # Prepare a list of image URLs to include in embeds
    attachment_urls = image_urls[:4]  # Adjust this as needed

    # Create a list of embeds
    embeds = []
    for i, img_url in enumerate(attachment_urls):
        result = web_search(query)
        description = (
            f':mag: **Search Query:** {query}\n\n'
            f'{result}'
        )
        embed = discord.Embed(description=description, color=0x99ccff, url="https://rajtech.me")
        try: user = interaction.user; avatar_url = interaction.user.avatar.url
        except AttributeError: user = interaction.author; avatar_url = interaction.author.avatar.url
        embed.set_footer(text=f"Requested by {user}", icon_url=avatar_url)

        # Set image in embed
        embed.set_image(url=img_url)
        embeds.append(embed)

    if not message:
        await interaction.followup.send(embed=embed)
    else:
        await channel.send(embeds=embeds, reference=message, mention_author=False)




# async def upload_image_to_discord(image_data, channel_id):
#     url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
    
#     headers = {
#         'Authorization': f'Bot MTI1MDEyODA5Nzk0MTAwMDIyMw.GxHB6g.W9LqL1XJDSGRjNcdcXBfFGxPnDCaCzZuyNd--A',
#         'Content-Type': 'multipart/form-data'
#     }
    
#     # Create a multipart form-data payload
#     data = aiohttp.FormData()
#     data.add_field('file', BytesIO(image_data), filename='image.png', content_type='image/png')
#     data.add_field('payload_json', '{"content": ""}')  # Adding an empty message payload
    
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, headers=headers, data=data) as response:
#             if response.status == 200:
#                 response_json = await response.json()
#                 return response_json['attachments'][0]['url']
#             else:
#                 print(f"Failed to upload image: {response.status} {await response.text()}")
#                 return None


async def vision(prompt, image_link):
    try:
        response = await openai_client.chat.completions.create(
            model="gemini-1.5-pro-latest",
            messages=[
            {
                "role": "user",
                "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                    "url": image_link
                    },
                },
                ],
            }
            ],

        )
        return response.choices[0].message.content
    except:
        return "Ouch! Something went wrong!"