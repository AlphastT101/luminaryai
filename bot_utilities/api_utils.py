import httpx
import random
import string
import smtplib
import requests
from openai import AsyncOpenAI
from email.mime.text import MIMEText
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart

system_prompt = {
    "gpt-4": "I am GPT-4. I am not GPT-4-Turbo rather I am a normal GPT-4 powered by OpenAI.",
    "gpt-4-turbo": "I am GPT-4-Turbo, powered by OpenAI. I am not GPT-4.",
    "gpt-3.5": "I am GPT-3.5. I Always try to act as a GPT-3.5. I am a normal version of GPT-3.5 means I am not the turbo edition. Plus, I am not GPT-4 or GPT-4-turbo.",
    "gpt-3.5-turbo": "I am GPT-3.5-turbo, I am not GPT-4-turbo. I am powered by OpenAI"
}

spml = ["gpt-4", "gpt-4-turbo", "gpt-3.5", "gpt-3.5-turbo"]
models_dict = {
    "gpt-4":"openchat/openchat-7b:free",
    "gpt-4-turbo":"openchat/openchat-7b:free",
    "gpt-3.5":"openchat/openchat-7b:free",
    "gpt-3.5-turbo":"openchat/openchat-7b:free",

    "mistral":"mistralai/mistral-7b-instruct:free",
    "llama-3":"meta-llama/llama-3-8b-instruct:free",
    "llama-3.1":"meta-llama/llama-3.1-8b-instruct:free",
    "gemma-2": "google/gemma-2-9b-it:free",

    # "gemma":"google/gemma-7b-it:free",
    # "qwen-2":"qwen/qwen-2-7b-instruct:free",
    # "phi-3-mini":"microsoft/phi-3-mini-128k-instruct:free",
    # "phi-3-medium":"microsoft/phi-3-medium-128k-instruct:free",
    # "nous-capybara":"nousresearch/nous-capybara-7b:free",
    # "mythomist":"gryphe/mythomist-7b:free",
    # "toppy-m":"undi95/toppy-m-7b:free",
    # "zephyr-beta":"huggingfaceh4/zephyr-7b-beta:free",

    # "gpt-4o":"1t",
}

available = [
'gpt-4', 'gpt-4-turbo', 'gpt-3.5', 'gpt-3.5-turbo',
'llama-3','llama-3.1', 'gemma-2', 'mistral'
]
# 'gpt-4o', 'command-r-plus-online'


async def poli(prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    response = requests.get(image_url)
    return response.url

async def generate_api_key(prefix='XET'):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    api_key = f'{prefix}-{random_string}'
    return api_key


async def check_token(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    collection_accounts = db['accounts_registered']

    result = collection.find_one({"apitoken": token})
    result_accounts = collection_accounts.find_one({"api_token": token})
    if result and not result_accounts: return True, True, None # discord user
    elif not result and result_accounts: return True, False, result_accounts['email'] # not a discord user
    else: return None, None, None

async def check_user(mongodb, userid):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    result = collection.find_one({"userid": userid})
    if result: return True
    else: return False

async def insert_token(mongodb, userid):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    key = await generate_api_key()
    collection.insert_one({"apitoken": key, "userid": userid})
    return key

async def delete_token(mongodb, userid):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    key = collection.delete_one({"userid": userid})
    return "deleted" if key else None

async def get_id(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    id_doc = collection.find_one({"apitoken": token})
    user_id = "None" if not id_doc["userid"] else id_doc["userid"]
    return user_id


async def gen_text(api_key, msg_history, model):
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_ = msg_history[0]["role"]
    if system_ == "system" and model in spml:
        msg_history.insert(0, {"role": "system", "name": model , "content": f"{system_prompt[model]} {system_}"})
    elif system_ != "system" and model in spml:
        msg_history.insert(0, {"role": "system","name": model, "content": system_prompt[model]})

    completion = await client.chat.completions.create(
        model=models_dict[model],
        messages=msg_history,
    )
    try:
        return completion.choices[0].message.content
    except Exception as e:
        return "A massive error occured, please try again a few moments later,"

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


async def delete_channel(channel_id, headers, httpx):
    async with httpx.AsyncClient() as client:
        try:
            req = await client.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
        except httpx.HTTPError as e:
            print(f"Failed to delete channel: {str(e)}")

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

async def log_image(user_id, engine, img_url, prompt, headers):
    async with httpx.AsyncClient() as client:
        try:

            embed = {
                "title": "Image Generated",
                "description": f"**User**: <@{user_id}>\n**Model:** {engine}\n\n **Prompt:**\n```{prompt}```",
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
            print(f"WARNING: FAILED TO LOG IMAGE, ERROR: {exc.response.text}")
        except Exception as e:
            print(f"WARNING: An unexpected error occurred: {str(e)}")

async def log_message(title, description, color, headers):
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
                f'https://discord.com/api/v9/channels/1318968624958013491/messages',
                json=data,
                headers=headers
            )
            req.raise_for_status()
        except httpx.HTTPStatusError as exc:
            print(f"WARNING: FAILED TO LOG IMAGE, ERROR: {exc.response.text}")
        except Exception as e:
            print(f"WARNING: An unexpected error occurred: {str(e)}")


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

async def get_engine_id(model, size):
    if model == "flux-dev":
        if size == "1024x1024": return "1280547383330996265"
        if size == "1024x576": return "1317112160178012211"
        if size == "1024x768": return "1317111418746572871"
        if size == "512x512": return "1309060402579243039"
        if size == "576x1024": return "1317054614205632582"
        if size == "768x1024": return "1309051413401436200"

    if model == "flux-schnell":
        if size == "1024x1024": return "1254085308614709318"
        if size == "1024x576": return "1317045818636898335"
        if size == "1024x768": return "1317042650573963316"
        if size == "512x512": return "1309091286912860190"
        if size == "576x1024": return "1317026958391119903"
        if size == "768x1024": return "1309093699631714364"

    if model == "sdxl-turbo":
        if size == "1024x1024": return "1265594684084981832"
        if size == "1024x576": return "1317120446285742171"
        if size == "1024x768": return "1317119334933594143"
        if size == "512x512": return "1309096880470233139"
        if size == "576x1024": return "1317118112512086127"
        if size == "768x1024": return "1309098603196846161"

    else: return "error"