import os
import jwt
import yaml
import time
import httpx
import random
import signal
import string
import logging
import asyncio
import warnings
from pydantic import BaseModel
from collections import defaultdict
from bot_utilities.api_utils import *
from bot_utilities.api_models import models
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from bot_utilities.start_util import api_start
from datetime import datetime, timedelta, timezone
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, status, BackgroundTasks

# Setup logging
logger = logging.getLogger("custom_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("error.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger.addHandler(file_handler)
logging.getLogger("uvicorn.error").propagate = False
logging.getLogger("uvicorn.error").handlers = []

warnings.filterwarnings("ignore", message="Using the in-memory storage for tracking rate limits")
warnings.filterwarnings("ignore", category=DeprecationWarning)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def sync_api_stats():
    global api_stats
    while True:
        await save_api_stats(api_stats, clientdb)
        api_stats = {}
        await asyncio.sleep(20)


with open("config.yml", "r") as config_file: 
    config = yaml.safe_load(config_file)

token_rate_limits = defaultdict(list)

guild_id = str(config["api"]["api_guild_id"])
guild_id_verify = str(config["api"]["verify_guild_id"])
verified_role_id = str(config['api']['verified_role_id'])
verification_email = config['api']['verification_email']

ALGORITHM = "HS256"
clientdb = MongoClient(config["bot"]["mongodb"])
clientdb['lumi-api']['accounts_registered'].create_index("expiresAt", expireAfterSeconds=0)
clientdb['lumi-api']['jwt_tokens'].create_index("expiration", expireAfterSeconds=0)
sbot = get_t_sbot(clientdb)
bot_token, open_r, jwt_secret, verify_email_pass= api_start(clientdb)

api_stats = {}
headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
sheader = {'Authorization': sbot}

@app.exception_handler(Exception)
async def custom_internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"An error occurred: {exc}")
    return JSONResponse(status_code=500, content={"error": "Sorry, we've hit the ratelimit, we're working on it to fix it :( "})

@app.get('/')
async def index():
    return "hi, what are you doing here? there is nothing to view in our api endpoint."

@app.get("/create-task")
async def create_task(request: Request):
    if request.client.host != "127.0.0.1" and request.client.host != "::1":
        return JSONResponse(status_code=403, content={"code": "403"})
    
    asyncio.create_task(sync_api_stats())
    print("API Engine has been started.") 
    return JSONResponse(status_code=200, content={"code": "200"})

@app.get("/shutdown")
async def shutdown(request: Request):
    if request.client.host != "127.0.0.1" and request.client.host != "::1":
        return JSONResponse(status_code=403, content={"code": "403"})
    
    print("Shutting down the server...")
    os.kill(os.getpid(), signal.SIGINT)

@app.post('/v1/images/generations')
async def image(request: Request, background_tasks: BackgroundTasks):

    try:
        token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else None
        if not token: return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "API token is not found in the JSON."})
        data = await request.json()
        prompt = data['prompt']
        engine = data['model']
        size = data['size']
    except KeyError: return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "You MUST include 'prompt', 'model', 'size' in the JSON."})
    except Exception as e:
        logger.error(f"An error occurred: {e}\n\n")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "An internal server error occured, please try again a few moments later."})

    if not engine in ["sdxl-turbo", "flux-dev", "flux-schnell", "poli"]:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail":"Unknown engine. Available engines are: 'sdxl-turbo', 'flux-dev', 'flux-schnell', 'poli'"})
    if not size in ['1024x1024', '1024x576', '1024x768', '512x512', '576x1024', '768x1024']:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail":"Unknown Size. Available sizes are: '1024x1024', '1024x576', '1024x768', '512x512', '576x1024', '786x1024'"})

    api_stats[engine] = api_stats.get(engine, 0) + 1 # API Stats + 1
    result, discord_user, email = await check_token(clientdb, token)
    if not result: return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Unauthorized, check your API token and try again."})

    current_time = time.time()
    if token.startswith("luminary") or token.startswith("XET"):
        token_rate_limits[token] = [timestamp for timestamp in token_rate_limits[token] if current_time - timestamp < 60]
        if len(token_rate_limits[token]) >= 100:
            return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Rate limit exceeded for this API token. 100/RPM"})
        token_rate_limits[token].append(current_time)

    # Fetch the userID and check if the user has the verified role or not, if user is owner, then skip verification.
    if discord_user:
        user_id = str(await get_id(clientdb, token))
        if not user_id.startswith('owner'):
            async with httpx.AsyncClient() as client:
                member_response = await client.get(f"https://discord.com/api/v10/guilds/{guild_id_verify}/members/{user_id}", headers=headers)
                member_data = member_response.json()
                user_roles = member_data.get('roles', [])
                if verified_role_id not in user_roles:
                    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail":"Your account is not verified/You left the XET server."})


    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(10))

    img_url = ""
    if engine == "poli":
        if size!= "1024x1024": return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "The specified size is not available for poli."})
        img_url = await poli(prompt)

    elif engine in ["sdxl-turbo", "flux-schnell", "flux-dev"]:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"https://discord.com/api/v9/guilds/{guild_id}/channels", json={"name": f"api-{random_string}", "permission_overwrites": [], "type": 0}, headers=headers)
            channel_info = res.json()
            channel_id = channel_info['id']
            engine_id = await get_engine_id(engine, size)
            if engine_id == "error": return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "The requested size is not available for this model."})
            seconds = 0
            retries = 0
            xRetries = 0
            error_ids = []
            checked = []
            do_break = False
            failed = False
            content = f"<@{engine_id}> !imagine {prompt}"
            await client.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', json={"content": content}, headers=sheader)

            while True:
                try:
                    res = await client.get(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers)
                    messages = res.json()
                    for message in messages:
                        message_id = message['id']
                        if message_id in checked: pass
                        elif message['content'] in ['error', 'uhh can you say that again?'] and message_id not in error_ids:
                            if retries > 3: failed = True
                            await client.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', json={"content": content}, headers=sheader)
                            retries += 1
                            error_ids.append(message_id)

                        elif message['content'].startswith("https://"):
                            img_url = message['content']
                            do_break = True
                            break
                        elif message['content'] != content and message_id not in checked:
                            if xRetries >= 3: failed = True
                            await client.post(f'https://discord.com/api/v9/channels/{channel_id}/messages', json={"content": content}, headers=sheader)
                            xRetries+=1

                        checked.append(message_id)

                    if do_break: break
                    elif failed or seconds >= 50:
                        background_tasks.add_task(delete_channel, channel_id, headers, httpx)
                        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "It's either shapes.inc faced a server error or the image content was NSFW."})
                    else:
                        seconds += 1.5
                        await asyncio.sleep(1.5)

                except Exception as e:
                    logger.error(f"An error occurred: {e}\n\n")
                    background_tasks.add_task(delete_channel, channel_id, headers, httpx)
                    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "An internal server error occurred."})

            background_tasks.add_task(delete_channel, channel_id, headers, httpx)

    logging_enabled = bool(config["api"]["logging"])

    if logging_enabled and email: background_tasks.add_task(log_image, email, engine, img_url, prompt, headers)
    else: background_tasks.add_task(log_image, user_id, engine, img_url, prompt, headers)
    return JSONResponse(content={"data": [{"url": img_url}]})



@app.post('/v1/chat/completions')
async def text(request: Request):
    try:
        token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else None
        if not token: return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Auth failed, API is token not found in the JSON."})
        data = await request.json()
        messages = data['messages']
        model = data['model']
    except KeyError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail":"You MUST include 'messages' and 'model' in the JSON."})
    if model not in available:return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "Model is not available."})

    api_stats[model] = api_stats.get(model, 0) + 1
    result, discord_user, email = await check_token(clientdb, token)
    if not result: return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid API token."})

    current_time = time.time()
    if token.startswith("luminary") or token.startswith("XET"):
        token_rate_limits[token] = [timestamp for timestamp in token_rate_limits[token] if current_time - timestamp < 60]
        if len(token_rate_limits[token]) >= 1:
            return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Rate limit exceeded for this API token. >1RPM"})

        token_rate_limits[token].append(current_time)

    # Fetch the userID and check if the user has the verified role or not, if user is owner, then skip verification.
    if discord_user:
        user_id = str(await get_id(clientdb, token))
        if not user_id.startswith('owner'):
            async with httpx.AsyncClient() as client:
                member_response = await client.get(f"https://discord.com/api/v10/guilds/{guild_id_verify}/members/{user_id}", headers=headers)
                member_data = member_response.json()
                user_roles = member_data.get('roles', [])
                if "1279261339574861895" not in user_roles:
                    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Your account is not verified."})

    response = await gen_text(open_r, messages, model)
    return JSONResponse(content={"choices": [{"message": {"content": response}}]})


@app.get('/v1/models')
async def model_list():
    return JSONResponse(content=models)


class FetchCredentials(BaseModel):
    email: str
    password: str

@app.post("/v1/auth/login")
async def login(request: Request, background_tasks: BackgroundTasks, login_request: FetchCredentials):
    valid = await verify_login_details(login_request.email, login_request.password, clientdb)
    if not valid:
        background_tasks.add_task(
            log_message,
            "User Failed To login",
            f"Email: `{login_request.email}`\n**Reason:** Invalid Credentials.",
            0xFF0000,
            headers
        )
        return JSONResponse(status_code=401, content={"error": "Invalid credentials"})

    # Generate JWT token
    access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=120)
    access_token = await create_access_token(
        jwt_secret,
        ALGORITHM,
        jwt,
        {"sub": login_request.email},
        access_token_expires
    )
    await insert_access_token(login_request.email, access_token, access_token_expires, clientdb)
    background_tasks.add_task(
        log_message,
        "User Logged in",
        f"Email: `{login_request.email}`",
        0x3498db,
        headers
    )
    return JSONResponse(status_code=200, content={"access_token": access_token, "expiration": str(access_token_expires)})

@app.post("/v1/auth/register")
async def login(request: Request, background_tasks: BackgroundTasks, register_request: FetchCredentials):

    verify_code_expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    code = random.randint(100000, 999999)
    register = await register_user(register_request.email, register_request.password, code, verify_code_expire, clientdb)
    if register == "already registered":
        background_tasks.add_task(
            log_message,
            "User Failed To register",
            f"Email: `{register_request.email}`\n**Reason:** Account already exists.",
            0xFF0000,
            headers
        )
        return JSONResponse(status_code=401, content={"error": "Account already registered."})

    code = await send_verify_email(register_request.email, verification_email, verify_email_pass, code)

    background_tasks.add_task(
        log_message,
        "User Registered",
        f"Email: `{register_request.email}`",
        0x00FF00,
        headers
    )
    return JSONResponse(status_code=200, content={"detail": "Account created as unverified."})


@app.post("/v1/auth/account/verify")
async def login(request: Request, background_tasks: BackgroundTasks):
    json = await request.json()
    email = json['email']
    code = json['verification_code']

    check = await check_verification_code(email, code, clientdb)

    if check == "verified":
        background_tasks.add_task(log_message, "User Verified", f"Email: `{email}`", 0x00FF00, headers)

        access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=120)
        access_token = await create_access_token(jwt_secret, ALGORITHM, jwt, {"sub": email}, access_token_expires)
        await insert_access_token(email, access_token, access_token_expires, clientdb)

        background_tasks.add_task(log_message, "User Logged in", f"Email: `{email}`", 0x3498db, headers)
        return JSONResponse(status_code=200, content={"detail": "Account verified.", "access_token": access_token, "exp": str(access_token_expires)})

    background_tasks.add_task(log_message, "User Failed To Verify", f"Email: `{email}`\n**Reason:** Invalid Verification code.", 0xFF0000, headers)
    return JSONResponse(status_code=401, content={"detail": "Invalid verification code."})

@app.post("/v1/account/info")
async def account_info(request: Request, background_tasks: BackgroundTasks):
    json = await request.json()
    if not await verify_access_token(json['jwt_token'], clientdb): return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
 
    email, logged_out_in = await get_account_info(json['jwt_token'], clientdb)
    name = email.split('@')[0]
    return JSONResponse(status_code=200, content={"name": name, "email": email, "logged_out_in": logged_out_in})

@app.post("/v1/api/stats")
async def api_statsss(request: Request, background_tasks: BackgroundTasks):
    json = await request.json()
    if not await verify_access_token(json['jwt_token'], clientdb): return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    stats = await get_api_stats(clientdb)
    return JSONResponse(status_code=200, content={"stats": stats})

@app.post("/v1/account/generate-token")
async def generate_token(request: Request, background_tasks: BackgroundTasks):
    json = await request.json()
    if not await verify_access_token(json['jwt_token'], clientdb): return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    
    token = await generate_api_key()
    email, logged_out_in = await get_account_info(json['jwt_token'], clientdb)
    await insert_account_token(token, email, clientdb)

    return JSONResponse(status_code=200, content={"token": token})

@app.post("/v1/account/delete-token")
async def generate_token(request: Request, background_tasks: BackgroundTasks):
    json = await request.json()
    if not await verify_access_token(json['jwt_token'], clientdb): return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    email, logged_out_in = await get_account_info(json['jwt_token'], clientdb)
    await delete_account_token(email, clientdb)
    return JSONResponse(status_code=200, content={"detail": "done"})

@app.post("/v1/account/tokens")
async def list_tokens(request: Request, background_tasks: BackgroundTasks):
    json = await request.json()
    if not await verify_access_token(json['jwt_token'], clientdb): return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    email, logged_out_in = await get_account_info(json['jwt_token'], clientdb)
    token = await list_token(email, clientdb)
    return JSONResponse(status_code=200, content={"token": token})


if __name__ == '__main__':

    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").disabled = True
    import uvicorn
    uvicorn.run(
        "api:app",
        host='0.0.0.0',
        port=int(os.environ.get("PORT", str(config["api"]["port"]))),
        log_level="critical",
    )