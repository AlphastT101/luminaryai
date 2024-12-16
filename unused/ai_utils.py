""" NOT USED, DO NOT REMOVE.
request_queue = asyncio.Queue()

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

async def vision(prompt, image_link, client):
    try:
        response = await client.chat.completions.create(
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
"""