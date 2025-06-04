import io
import bs4
import random
import discord
import requests

async def poli(session, prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&nologo=true"
    async with session.get(image_url) as response:
        image_data = await response.read()
        return io.BytesIO(image_data)

async def gentext(history):
    headers = {
        "Authorization": "Bearer TRYBrn1QIiyYYkQ2",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai-large",
        "private": True,
        "messages": history
    }

    response = requests.post("https://text.pollinations.ai/", json=data, headers=headers)
    return response.text

def web_search(query):
    api_url = 'https://api.duckduckgo.com/'
    params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1
    }
    try:
        response = requests.get(api_url, params=params)
        data = response.json()
        if 'AbstractText' in data: result = data['AbstractText']
        elif 'Definition' in data: result = data['Definition']
        else: result = None
        return result
    except requests.RequestException as e:
        return f"An error occurred: {e}"

async def search_image(query):
    search_url = f"https://www.bing.com/images/search?q={query}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        image_tags = soup.find_all('img', {'class': 'mimg'})
        image_urls = [img['src'] for img in image_tags[:4]]
        
        return image_urls
    except requests.exceptions.RequestException as e:
        print(f"Error searching for images: {e}")
        return None

async def create_and_send_embed(query, image_urls, message, interaction):

    attachment_urls = image_urls[:4]

    embeds = []
    for i, img_url in enumerate(attachment_urls):
        result = web_search(query)
        description = (
            f':mag: **Search Query:** {query}\n\n'
            f'{result}'
        )
        embed = discord.Embed(description=description, url="https://xet.one")
        try: user = interaction.user; avatar_url = interaction.user.avatar.url
        except AttributeError: user = interaction.author; avatar_url = interaction.author.avatar.url
        embed.set_footer(text=f"Requested by {user}", icon_url=avatar_url)

        embed.set_image(url=img_url)
        embeds.append(embed)

    if not message:
        await interaction.followup.send(embeds=embeds)
    else:
        await message.edit(embeds=embeds)