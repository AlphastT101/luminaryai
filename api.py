import io
import os
import yaml
import time
import random
import string
import logging
import warnings
import httpx
import asyncio
from PIL import Image
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from pymongo.mongo_client import MongoClient

from bot_utilities.start_util import start
from bot_utilities.api_models import models
from bot_utilities.api_utils import poli, gen_text, check_token, get_id, get_t_sbot, available

# Setup logging
log = logging.getLogger('uvicorn')
warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")
log.setLevel(logging.ERROR)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration
with open("config.yml", "r") as config_file:
    global config
    config = yaml.safe_load(config_file)
flask_port = str(config["flask"]["port"])
token_rate_limits = defaultdict(list) # Rate limit dictionaries

@app.on_event("startup")
async def startup_event():
    global clientdb, sbot, bot_token, open_r, mongodb, guild_id, guild_id_verify, send_req, webhook
    print("INFO: API engine has started, loading utils...")

    mongodb = config["bot"]["mongodb"]
    guild_id = str(config["flask"]["guild_id"])
    webhook = str(config["bot"]["webhook_images"])
    send_req = str(config["flask"]["send_req_channel"])
    guild_id_verify = str(config["flask"]["guild_id_verify"])

    clientdb = MongoClient(mongodb)
    sbot = get_t_sbot(clientdb)
    bot_token, open_r = start(clientdb)

    cache_folder = os.path.join(os.getcwd(), 'cache')
    os.makedirs(cache_folder, exist_ok=True)

    print("INFO: Utils are loaded. API is now functional.")

@app.get('/')
async def index():
    return "hi, what are you doing here? there is nothing to view in our api endpoint."

@app.post('/v1/images/generations')
async def image(request: Request):

    # get token, prompt, model from the json
    try:
        token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else None
        if not token: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth failed, API is token not found in the JSON.")
        data = await request.json()
        prompt = data['prompt']
        engine = data['model']
    except KeyError: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You MUST include 'prompt' and 'model' in the JSON.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An internal server error occured, please try again a few moments later.")

    # Check token validity
    result = await check_token(clientdb, token)
    if not result: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token!")

    # Rate limiting by token
    current_time = time.time()
    if token.startswith("luminary"):
        token_rate_limits[token] = [timestamp for timestamp in token_rate_limits[token] if current_time - timestamp < 60]
        if len(token_rate_limits[token]) >= 200:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded for this API token.")
        token_rate_limits[token].append(current_time)

    # variables to make requests to discord api
    headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
    sheader = {'Authorization': sbot}

    # Fetch the userID and check if the user has the verified role or not, if user is owner, then skip verification.
    user_id = str(await get_id(clientdb, token))
    if not user_id.startswith('owner'):
        async with httpx.AsyncClient() as client:
            member_response = await client.get(f"https://discord.com/api/v10/guilds/{guild_id_verify}/members/{user_id}", headers=headers)
            member_data = member_response.json()
            user_roles = member_data.get('roles', [])
            if "1279261339574861895" not in user_roles: # 1279261339574861895 is the role id, DO NOT CHANGE IT
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your account is not verified.")

    # Now, the user is verified, ratelimits are not exceed, token is valid. Continue to generate the image.
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(12))

    img_url = ""
    if engine == "poli":
        img_url = await poli(prompt)
    elif engine in ["sdxl-turbo", "dalle3", "flux"]:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"https://discord.com/api/v9/guilds/{guild_id}/channels", json={"name": f"api-{random_string}", "permission_overwrites": [], "type": 0}, headers=headers)
            channel_info = res.json()
            channel_id = channel_info['id']
            engine_id = "1254085308614709318" if engine == "dalle3" else "1265594684084981832" if engine == "sdxl-turbo" else "1280547383330996265"
            seconds = 0
            await client.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', json={"content": f"<@{engine_id}> Generate an image of {prompt}"}, headers=sheader)

            while True:
                res = await client.get(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers)
                messages = res.json()
                do_break = False
                failed = False
                for message in messages:
                    if message['content'].startswith("https://"): # generated image URL starts with https://
                        img_url = message['content']
                        do_break = True
                        break
                    elif message['content'] == "error": # the bot returns "error" when it fails
                        failed = True

                if do_break: # break when the image generation is done
                    break
                elif failed: # return 500 if failed
                    await client.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred.")
                elif seconds >= 80: # if it takes more than 80 seconds to generate the image, then it's probably failed
                    await client.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
                    raise HTTPException(status_code=status.HTTP_520_UNKNOWN_ERROR, detail="An error occurred, this is probably our fault.")
                else:
                    seconds += 1
                    await asyncio.sleep(1)
            await client.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers) # delete after generation
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown engine.")

    upload2discord = bool(config["flask"]["upload2discord"])
    logging_enabled = bool(config["flask"]["logging"])

    if upload2discord:
        async with httpx.AsyncClient() as client:
            img_response = await client.get(img_url)
            img = Image.open(io.BytesIO(img_response.content))
            img_io = io.BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            file_path = os.path.join('cache', f'{random_string}.png')
            with open(file_path, 'wb') as f:
                f.write(img_io.getbuffer())
            with open(file_path, 'rb') as f:
                response = await client.post(webhook, files={'file': f})
            response = response.json()
            img_url = response['attachments'][0]['url']
            os.remove(file_path)

    if logging_enabled:
        async with httpx.AsyncClient() as client:
            try:
                req = await client.post(
                    f'https://discord.com/api/v9/channels/1279262113503645706/messages',
                    json={"content": f"<@{user_id}> | {engine}\n`{img_url}`\n\n`{prompt}`"},
                    headers=headers
                )
                req.raise_for_status()  # Raises an error for bad responses (4xx and 5xx)
            except httpx.HTTPStatusError as exc:
                print(f"WARNING: FAILED TO LOG IMAGE, ERROR: {exc.response.text}")
            except Exception as e:
                print(f"WARNING: An unexpected error occurred: {str(e)}")


    return JSONResponse(content={"data": [{"url": img_url}, {"serveo": f"https://xet.serveo.net/cache/{random_string}.png"}]})




@app.post('/v1/chat/completions')
async def text(request: Request):

    # get token, messages, model from the json
    try:
        token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else None
        if not token: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Auth failed, API is token not found in the JSON.")
        data = await request.json()
        messages = data['messages']
        model = data['model']
        if model not in available: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model is not available.")
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You MUST include 'messages' and 'model' in the JSON.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="An internal server error occured, please try again a few moments later.")

    # Check token validity
    result = await check_token(clientdb, token)
    if not result: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token!")

    # Rate limiting logic by token
    current_time = time.time()
    if token.startswith("luminary"):
        token_rate_limits[token] = [timestamp for timestamp in token_rate_limits[token] if current_time - timestamp < 60]
        if len(token_rate_limits[token]) >= 15:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded for this API token. >15RPS")

        token_rate_limits[token].append(current_time)

    # Fetch the userID and check if the user has the verified role or not, if user is owner, then skip verification.
    user_id = str(await get_id(clientdb, token))
    headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
    if not user_id.startswith('owner'):
        async with httpx.AsyncClient() as client:
            member_response = await client.get(f"https://discord.com/api/v10/guilds/{guild_id_verify}/members/{user_id}", headers=headers)
            member_data = member_response.json()
            user_roles = member_data.get('roles', [])
            if "1279261339574861895" not in user_roles:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Your account is not verified.")

    # Now, the user is verified, ratelimits are not exceed, token is valid. Continue to text generation.
    response = await gen_text(open_r, messages, model)
    return JSONResponse(content={"choices": [{"message": {"content": response}}]})


@app.get('/v1/models')
async def model_list():
    return JSONResponse(content=models)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", flask_port))
    import uvicorn
    uvicorn.run("api:app", host='0.0.0.0', port=port, log_level="warning")