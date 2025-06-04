import os
import jwt
import yaml
import time
import signal
import random
import logging
import asyncio
import warnings
import traceback
from openai import AsyncOpenAI
from pydantic import BaseModel
from datetime import timedelta
from collections import defaultdict
from api_utilities.api_utils import *
from pymongo.mongo_client import MongoClient
from api_utilities.start_util import api_start
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi import FastAPI, Request, status, BackgroundTasks, Query

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

openrouter = AsyncOpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="konnichiwaaaAAA",
)

async def sync_api_stats():
    global api_stats
    global available

    while True:
        await save_api_stats(api_stats, clientdb)
        available = await fawom()
        api_stats = {}
        await asyncio.sleep(20)

with open("config.yml", "r") as config_file: 
    config = yaml.safe_load(config_file)

token_rate_limits = defaultdict(list)
guild_id = str(config["api"]["api_guild_id"])
verification_email = config['api']['verification_email']

ALGORITHM = "HS256"
clientdb = MongoClient(config["bot"]["mongodb"])
clientdb['lumi-api']['accounts_registered'].create_index("expiresAt", expireAfterSeconds=0)
clientdb['lumi-api']['jwt_tokens'].create_index("expiration", expireAfterSeconds=0)
bot_token, jwt_secret, verify_email_pass, action_password = api_start(clientdb)
sbot = get_t_sbot(clientdb)

available = None
api_stats = {}
headers = {"Authorization": f"Bot {bot_token}", "Content-Type": "application/json"}
sheader = {'Authorization': sbot}

@app.exception_handler(Exception)
async def custom_internal_server_error_handler(request: Request, exc: Exception):

    tb_list = traceback.extract_tb(exc.__traceback__)
    your_code_frame = next(
        (frame for frame in reversed(tb_list) 
         if 'site-packages' not in frame.filename and 
            'python3.13' not in frame.filename),
        None
    )
    
    if your_code_frame:
        logger.error(
            f"\nError in {your_code_frame.name}() at {your_code_frame.filename}:{your_code_frame.lineno}\n"
            f"Code: {your_code_frame.line}\n"
            f"Error: {type(exc).__name__}: {str(exc)}\n\n"
        )
    else:
        logger.error(f"Error: {type(exc).__name__}: {str(exc)}")
    
    return JSONResponse(status_code=500, content={"error": "Internal server error",})

@app.get('/')
async def index():
    return "hi, what are you doing here?"

@app.get("/files/{image_name}")
async def serve_image(image_name: str):

    image_path = os.path.join("cache", image_name)
    if os.path.isfile(image_path): return FileResponse(image_path)
    return JSONResponse(status_code=404, content={"code": "404", "message": "not found"})

@app.get("/create-task")
async def create_task(request: Request, pass_: str = Query(None, alias="pass")):
    if pass_ != action_password:
        return JSONResponse(status_code=403, content={"code": "403", "message": "Forbidden"})
    
    asyncio.create_task(sync_api_stats())
    print("API stats sync task has been started.") 
    return JSONResponse(status_code=200, content={"code": "200", "message": "Task started successfully"})

@app.get("/shutdown")
async def shutdown(request: Request, pass_: str = Query(None, alias="pass")):

    if pass_ != action_password:
        return JSONResponse(status_code=403, content={"code": "403", "message": "Forbidden"})
    
    print("Shutting down the server...")
    os.kill(os.getpid(), signal.SIGINT)

@app.post('/v1/images/generations')
async def image(request: Request, background_tasks: BackgroundTasks):

    try:
        token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else None
        data = await request.json()
        prompt = data['prompt']
        model = data['model']
        size = data['size']
    except KeyError: return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "You MUST include 'prompt', 'model', 'size' and API token in the JSON."})
    except Exception as e: return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "An internal server error occured, please try again a few moments later."})

    if not model in ["sdxl-turbo", "flux"]:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail":"Unknown model. Available models are: 'sdxl-turbo'"})
    if not size in ['1024x1024', '1024x576', '1024x768', '512x512', '576x1024', '768x1024']:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail":"Unknown Size. Available sizes are: '1024x1024', '1024x576', '1024x768', '512x512', '576x1024', '786x1024'"})

    api_stats[model] = api_stats.get(model, 0) + 1 # API Stats + 1
    result, email = await check_token(clientdb, token)
    if not result: return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Unauthorized, check your API token and try again."})

    current_time = time.time()
    if token.startswith("luminary") or token.startswith("XET"):
        token_rate_limits[token] = [timestamp for timestamp in token_rate_limits[token] if current_time - timestamp < 60]
        if len(token_rate_limits[token]) >= 5:
            return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Rate limit exceeded for this API token. >5/RPM"})
        token_rate_limits[token].append(current_time)

    img_url = ""

    if size != "1024x1024": return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "The specified size is not available for this model."})
    img_url = await poli(prompt, model)

    logging_enabled = bool(config["api"]["logging"])
    if logging_enabled:
        background_tasks.add_task(log_image, email, model, img_url, prompt, headers)

    return JSONResponse(content={"data": [{"url": f"https://api.xet.one/files/{img_url}"}]})


@app.post('/v1/chat/completions')
async def text(request: Request, background_tasks: BackgroundTasks):
    try:
        token = request.headers.get('Authorization', '').split()[1] if 'Authorization' in request.headers else None
        data = await request.json()
        messages = data['messages']
        model = data['model']
    except KeyError:
        return JSONResponse(status_code=400, content={"error":"You MUST include 'messages', 'model' and API token in the JSON."})

    api_stats[model] = api_stats.get(model, 0) + 1
    result, email = await check_token(clientdb, token)
    if not result: return JSONResponse(status_code=401, content={"error": "Invalid API token."})

    if model not in available:
        background_tasks.add_task(log_message, 'Request from unavailable model', f'**Model**: {model}\n**User**: {email}\n\n**Prompt**:\n`{messages}`', 0x00FF00, headers, 1344331989599387680)
        return JSONResponse(status_code=404, content={"error": "unavailable model."})

    current_time = time.time()
    if token.startswith("luminary") or token.startswith("XET"):
        token_rate_limits[token] = [timestamp for timestamp in token_rate_limits[token] if current_time - timestamp < 60]
        if len(token_rate_limits[token]) >= 5:
            return JSONResponse(status_code=429, content={"error": "Rate limit exceeded for this API token. >5RPM"})

        token_rate_limits[token].append(current_time)

    completion = await openrouter.chat.completions.create(model=model, messages=messages)
    jsonr = completion.model_dump()

    return JSONResponse(content=jsonr)



# DASHBOARD ROUTES

@app.get('/v1/models')
async def model_list():
    return JSONResponse(content=available)

class FetchCredentials(BaseModel):
    email: str
    password: str

@app.post("/v1/auth/login")
async def login(request: Request, background_tasks: BackgroundTasks, login_request: FetchCredentials):
    valid = await verify_login_details(login_request.email, login_request.password, clientdb)
    if not valid:
        background_tasks.add_task(log_message, "User Failed To login", f"Email: `{login_request.email}`\n**Reason:** Invalid Credentials.", 0xFF0000, headers)
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
    background_tasks.add_task(log_message, "User Logged in", f"Email: `{login_request.email}`", 0x3498db, headers)
    return JSONResponse(status_code=200, content={"access_token": access_token, "expiration": str(access_token_expires)})

@app.post("/v1/auth/register")
async def login(request: Request, background_tasks: BackgroundTasks, register_request: FetchCredentials):

    verify_code_expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    code = random.randint(100000, 999999)
    register = await register_user(register_request.email, register_request.password, code, verify_code_expire, clientdb)
    if register == "already registered":
        background_tasks.add_task(log_message, "User Failed To register", f"Email: `{register_request.email}`\n**Reason:** Account already exists.", 0xFF0000, headers)
        return JSONResponse(status_code=401, content={"error": "Account already registered."})

    code = await send_verify_email(register_request.email, verification_email, verify_email_pass, code)

    background_tasks.add_task(log_message, "User Registered", f"Email: `{register_request.email}`", 0x00FF00, headers)
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
    print("API starting...")
    import uvicorn
    uvicorn.run(
        "api:app",
        host='0.0.0.0',
        port=int(os.environ.get("PORT", str(config["api"]["port"]))),
        log_level="critical",
    )