import httpx
import random
import string
import smtplib
import requests
from email.mime.text import MIMEText
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart

available = [
'qwen/qwen3-0.6b-04-28:free', 'qwen/qwen3-1.7b:free', 'qwen/qwen3-4b:free', 'opengvlab/internvl3-14b:free', 'opengvlab/internvl3-2b:free', 'deepseek/deepseek-prover-v2:free',
'qwen/qwen3-30b-a3b:free', 'qwen/qwen3-8b:free', 'qwen/qwen3-14b:free', 'qwen/qwen3-32b:free', 'qwen/qwen3-235b-a22b:free', 'tngtech/deepseek-r1t-chimera:free',
'thudm/glm-z1-9b:free', 'thudm/glm-4-9b:free', 'microsoft/mai-ds-r1:free', 'thudm/glm-z1-32b:free', 'thudm/glm-4-32b:free', 'shisa-ai/shisa-v2-llama3.3-70b:free',
'arliai/qwq-32b-arliai-rpr-v1:free', 'agentica-org/deepcoder-14b-preview:free', 'moonshotai/kimi-vl-a3b-thinking:free', 'nvidia/llama-3.3-nemotron-super-49b-v1:free',
'nvidia/llama-3.1-nemotron-ultra-253b-v1:free', 'meta-llama/llama-4-maverick:free', 'meta-llama/llama-4-scout:free', 'deepseek/deepseek-v3-base:free', 'allenai/molmo-7b-d:free',
'bytedance-research/ui-tars-72b:free', 'qwen/qwen2.5-vl-3b-instruct:free', 'google/gemini-2.5-pro-exp-03-25', 'qwen/qwen2.5-vl-32b-instruct:free',
'deepseek/deepseek-chat-v3-0324:free', 'featherless/qwerky-72b:free', 'mistralai/mistral-small-3.1-24b-instruct:free', 'open-r1/olympiccoder-32b:free', 'google/gemma-3-1b-it:free',
'google/gemma-3-4b-it:free', 'google/gemma-3-12b-it:free', 'rekaai/reka-flash-3:free', 'google/gemma-3-27b-it:free', 'deepseek/deepseek-r1-zero:free', 'qwen/qwq-32b:free',
'moonshotai/moonlight-16b-a3b-instruct:free', 'nousresearch/deephermes-3-llama-3-8b-preview:free', 'cognitivecomputations/dolphin3.0-r1-mistral-24b:free',
'cognitivecomputations/dolphin3.0-mistral-24b:free', 'qwen/qwen2.5-vl-72b-instruct:free', 'mistralai/mistral-small-24b-instruct-2501:free',
'deepseek/deepseek-r1-distill-qwen-32b:free', 'deepseek/deepseek-r1-distill-qwen-14b:free', 'deepseek/deepseek-r1-distill-llama-70b:free', 'deepseek/deepseek-r1:free',
'deepseek/deepseek-chat:free', 'google/gemini-2.0-flash-exp:free', 'meta-llama/llama-3.3-70b-instruct:free', 'qwen/qwq-32b-preview:free', 'google/learnlm-1.5-pro-experimental:free',
'qwen/qwen-2.5-coder-32b-instruct:free', 'qwen/qwen-2.5-7b-instruct:free', 'meta-llama/llama-3.2-3b-instruct:free', 'meta-llama/llama-3.2-1b-instruct:free',
'meta-llama/llama-3.2-11b-vision-instruct:free', 'qwen/qwen-2.5-72b-instruct:free', 'qwen/qwen-2.5-vl-7b-instruct:free', 'google/gemini-flash-1.5-8b-exp',
'meta-llama/llama-3.1-405b:free', 'meta-llama/llama-3.1-8b-instruct:free', 'mistralai/mistral-nemo:free', 'google/gemma-2-9b-it:free', 'mistralai/mistral-7b-instruct:free',
'huggingfaceh4/zephyr-7b-beta:free'
]

async def poli(prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}&nologo=true"
    response = requests.get(image_url)
    return response.url

async def generate_api_key():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    api_key = f'XET-{random_string}'
    return api_key

async def check_token(mongodb, token):
    collection_accounts = mongodb["lumi-api"]['accounts_registered']
    result_accounts = collection_accounts.find_one({"api_token": token})
    if result_accounts: return True, result_accounts['email']
    else: return False, None

async def save_api_stats(new_api_stats, mongodb):
    db = mongodb['lumi-api']
    collection = db['stats']
    stats = collection.find_one({"key": "api_stats"})
 
    if stats is None:
        existing_stats = {}
    else:
        existing_stats = stats.get("value", {})
    
    for key, new_value in new_api_stats.items():
        if key in existing_stats:
            existing_stats[key] += new_value  # Increment existing value
        else:
            existing_stats[key] = new_value  # Add new key-value pair
    
    collection.update_one(
        {"key": "api_stats"},
        {"$set": {"value": existing_stats}},
        upsert=True  # Create a new document if it doesn't exist
    )

    return existing_stats

def get_t_sbot(mongodb):
    db = mongodb['tokens']
    collection = db['bot']
    sbot = collection.find_one({"key": "sbot"})
    
    if sbot is None:
        print("sBot: 404 Not Found, enter password for sbot:")
        sbot_value = input("> ")
        collection.insert_one({"key": "sbot", "value": sbot_value})
        return sbot_value

    else:
        return sbot['value']

async def delete_channel(channel_id, headers):
    async with httpx.AsyncClient() as client:
        try:
            await client.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
        except Exception as e:
            print(f"ERROR delete_channel(): {e}")

async def get_api_stat(mongodb):
    db = mongodb['lumi-api']
    collection = db['stats']
    stats = collection.find_one({"key": "api_stats"})

    if stats and 'value' in stats:
        model_stats = stats['value']
        formatted_stats = []

        for model_name, total_requests in model_stats.items():
            formatted_stats.append(f"**{model_name}:** `{total_requests}`")

        return "\n".join(formatted_stats)
    else:
        return "No API stats found."

async def log_image(email, engine, img_url, prompt, headers):
    async with httpx.AsyncClient() as client:
        try:

            embed = {
                "title": "Image Generated",
                "description": f"**User**: {email}\n**Model:** {engine}\n\n **Prompt:**\n```{prompt}```",
                "color": 0x3498db,  # Blue color
                "image": {"url": img_url},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            data = {"embeds": [embed]} # Embed must be sent inside a list
            req = await client.post(
                f'https://discord.com/api/v9/channels/1279262113503645706/messages',
                json=data,
                headers=headers
            )
            req.raise_for_status()
        except httpx.HTTPStatusError as exc:
            print("Error in api_utils.py at line 145.")
            print(f"WARNING: FAILED TO LOG IMAGE, ERROR: {exc.response.text}")
        except Exception as e:
            print("Error in api_utils.py at line 147.")
            print(f"WARNING: An unexpected error occurred: {str(e)}")

async def log_message(title, description, color, headers, channel_id=None):
    async with httpx.AsyncClient() as client:
        try:

            embed = {
                "title": title,
                "description": description,
                "color": color,  # Blue color
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            data = {"embeds": [embed]}
            req = await client.post(
                f'https://discord.com/api/v9/channels/{channel_id or "1318968624958013491"}/messages',
                json=data,
                headers=headers
            )
            req.raise_for_status()
        except httpx.HTTPStatusError as exc:
            print(f"Error while trying to log message: {exc.response.text}")
        except Exception as e:
            print(f"Error while trying to log message: {str(e)}")


async def create_access_token(SECRET_KEY, ALGORITHM, jwt, data, expires_delta):
    to_encode = data.copy()

    to_encode.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def insert_access_token(email, token, expiration, mongodb):
    db = mongodb['lumi-api']
    collection = db['jwt_tokens']
    collection.update_one(
        {"email": email},  # Filter by email
        {"$set": {
            "jwt_access_token": token,
            "expiration": expiration
        }},
        upsert=True  # Insert a new document if no match is found
    )

async def verify_access_token(token, mongodb):
    try:
        db = mongodb['lumi-api']
        collection = db['jwt_tokens']
        doc = collection.find_one({"jwt_access_token": token})
        
        if doc: return True
        else: return False
    except Exception as e:
        return False

async def verify_login_details(email, password, mongodb):
    try:
        db = mongodb['lumi-api']
        collection = db['accounts_registered']
        doc = collection.find_one({"email": email})

        if doc is None: return None
        if password != doc['password']: return None
        if doc['verified'] is False: return None
        else: return True
    except Exception as e:
        return None

async def register_user(email, password, verification_code, exp,  mongodb):
    db = mongodb['lumi-api']
    collection = db['accounts_registered']

    # Check if the user exists
    doc = collection.find_one({"email": email})
    if doc:
        if doc.get('verified'):
            return "already registered"
        # Update the existing document if not verified
        collection.update_one(
            {"email": email},
            {"$set": {
                "password": password,
                "verification_code": verification_code,
                "expiresAt": exp,
                "created_on": datetime.now(timezone.utc)
            }}
        )
        return "verification code updated"

    # Insert a new document if user doesn't exist
    collection.insert_one({
        "email": email,
        "password": password,
        "verified": False,
        "verification_code": verification_code,
        "expiresAt": exp,
        "created_on": datetime.now(timezone.utc)
    })
    return "registered as unverified"

async def check_verification_code(email, code, mongodb):
    try:
        db = mongodb['lumi-api']
        collection = db['accounts_registered']
        doc = collection.find_one({"email": email})

        if str(doc['verification_code']) == code:
            password = doc['password']
            created_on = doc['created_on']
            collection.delete_one({"email": email})
            collection.insert_one({
                "email": email,
                "password": password,
                "verified": True,
                "created_on": created_on
            })
            return "verified"
        else: return "unverified"
    except Exception as e:
        return "unverified"


async def send_verify_email(to_email, email_from, password, code):
    subject = "XET - Email verification"
    body = f"""
    <html>
    <body>
        <h2 style="color: #4CAF50;">Email Verification</h2>
        <p>Hello,</p>
        <p>Thank you for registering with us. The code below is valid only for 5 minutes. To complete your registration, please verify your email address by entering the following 6-digit code:</p>
        <h3 style="color: #FF5733; font-size: 30px;">{code}</h3>
        <p>If you did not request this verification, please ignore this email.</p>
        <p>Best regards,<br>XET</p>
    </body>
    </html>
    """
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = email_from
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP('smtp.zoho.com', 587) as server:
        server.starttls()
        server.login(email_from, password)
        server.send_message(msg)
    return code

from datetime import timezone

async def get_account_info(jwt_token, mongodb):
    db = mongodb['lumi-api']
    collection = db['jwt_tokens']
    doc = collection.find_one({"jwt_access_token": jwt_token})
    email = doc['email']

    exp = str(doc['expiration'])
    given_datetime = datetime.fromisoformat(exp).replace(tzinfo=timezone.utc)  # Make it aware
    current_datetime = datetime.now(timezone.utc)  # Already aware
    time_difference = given_datetime - current_datetime
    hours, remainder = divmod(time_difference.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)

    logged_out_in = f"{hours} hour(s), {minutes} minute(s)"
    return email, logged_out_in

async def insert_account_token(token, email, mongodb):
    db = mongodb['lumi-api']
    collection = db['accounts_registered']
    doc = collection.find_one({"email": email})
    password = doc['password']
    collection.delete_one({"email": email})
    collection.insert_one({
        "email":  email,
        "password": password,
        "verified": True,
        "api_token": token
    })
async def delete_account_token(email, mongodb):
    db = mongodb['lumi-api']
    collection = db['accounts_registered']
    doc = collection.find_one({"email": email})
    password = doc['password']
    collection.delete_one({"email": email})
    collection.insert_one({
        "email": email,
        "password": password,
        "verified": True
    })

async def list_token(email, mongodb):
    db = mongodb['lumi-api']
    collection = db['accounts_registered']
    doc = collection.find_one({"email": email})

    try:
        return doc['api_token']
    except KeyError: return None

async def get_api_stats(mongodb):
    db = mongodb['lumi-api']
    collection = db['stats']
    doc = collection.find_one({"key": "api_stats"})
    return doc['value']