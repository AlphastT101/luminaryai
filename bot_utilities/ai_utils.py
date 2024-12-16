async def image_generate(model, prompt, size, bot):
    if size is None: size = "1024x1024"
    response = await bot.xet_client.images.generate(
        prompt=prompt,
        model=model,
        size=size
    )
    return response.data[0].url

async def poly_image_gen(session, prompt, bot):
    seed = bot.modules_random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    async with session.get(image_url) as response:
        image_data = await response.read()
        return bot.modules_io.BytesIO(image_data)

def web_search(query, bot):
    api_url = 'https://api.duckduckgo.com/'
    params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1
    }
    try:
        response = bot.modules_requests.get(api_url, params=params)
        data = response.json()
        if 'AbstractText' in data: result = data['AbstractText']
        elif 'Definition' in data: result = data['Definition']
        else: result = None
        return result
    except bot.modules_requests.RequestException as e:
        return f"An error occurred: {e}"

def search_image(query, bot):
    search_url = f"https://www.bing.com/images/search?q={query}"
    try:
        response = bot.modules_requests.get(search_url)
        response.raise_for_status()
        soup = bot.modules_bs4.BeautifulSoup(response.text, 'html.parser')

        # Find all image tags
        image_tags = soup.find_all('img', {'class': 'mimg'})
        image_urls = [img['src'] for img in image_tags[:10]]
        
        return image_urls
    except bot.modules_requests.exceptions.RequestException as e:
        print(f"Error searching for images: {e}")
        return None



async def create_and_send_embed(discord, query, interaction, image_urls, bot, target_size=(256, 256)):

    channel = bot.get_channel(interaction.channel.id)
    try: message = await channel.fetch_message(interaction.message.id)
    except AttributeError: message = None

    # Helper function to check for duplicates
    def is_duplicate(img_hash, img_cv):
        for buffer in buffers:
            similarity = bot.modules_cv2.matchTemplate(buffer, img_cv, bot.modules_cv2.TM_CCOEFF_NORMED)
            if bot.modules_np.max(similarity) > 0.15:
                return True
        return False

    images = []
    hashes = set()
    buffers = []

    async with bot.modules_aiohttp.ClientSession() as session:
        for url in image_urls:
            try:
                async with session.get(url) as response:
                    content_type = response.headers.get('Content-Type') # Get the content type from the response headers
                    if content_type and 'image' in content_type:
                        img_data = await response.read()
                        
                        # Special handling for GIFs
                        if 'gif' in content_type:
                            images.append((img_data, 'gif'))
                            continue

                        img = bot.modules_PIL.Image.open(bot.modules_io.BytesIO(img_data))
                        img = img.resize(target_size, bot.modules_PIL.Image.LANCZOS)

                        # Convert image to numpy array for OpenCV
                        img_cv = bot.modules_np.array(img)
                        img_cv = bot.modules_cv2.cvtColor(img_cv, bot.modules_cv2.COLOR_RGB2BGR)

                        # Calculate image hash
                        img_hash = bot.modules_imagehash.average_hash(img)

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