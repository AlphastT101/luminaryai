import json
import httpx
import random
import string
import smtplib
import aiohttp
import requests
from pathlib import Path
from typing import Optional, Dict
from email.mime.text import MIMEText
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart

async def poli(prompt, model, cache="cache"):
    Path(cache).mkdir(exist_ok=True)
    url = f"https://image.pollinations.ai/prompt/{prompt}?seed={random.randint(1,100000)}&model={model}&nologo=true"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                ext = '.jpg' if 'jpeg' in r.headers.get('Content-Type','') else '.png'
                filename = f"{random.getrandbits(64):x}{ext}"
                path = f"{cache}/{filename}"
                open(path,'wb').write(await r.read())
                return filename
    except:
        return url

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
            print("Error in api_utils.py at line 120.")
            print(f"WARNING: FAILED TO LOG IMAGE, ERROR: {exc.response.text}")
        except Exception as e:
            print("Error in api_utils.py at line 123.")
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


async def fawom(output_path: str = "api_utilities/api_models.py") -> Optional[Dict]:
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        response.raise_for_status()
        models_data = response.json()

        free_models = []
        for model in models_data.get('data', []):
            pricing = model.get('pricing', {})
            if pricing.get('prompt') == "0" and pricing.get('completion') == "0":
                model_id = model.get('id', '').replace(':free', '')
                owned_by = model_id.split('/')[0] if '/' in model_id else model_id
                
                free_models.append({"id": model_id,"object": "model","created": 0,"owned_by": owned_by,"pricing": "free"})
        
        # Sort models by provider and name
        free_models.sort(key=lambda x: x['id'])

        output_data = {
            "object": "list",
            "data": free_models
        }

        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write('"""\n')
                f.write('Auto-generated list of free models from OpenRouter\n')
                f.write(f'Generated by fawom() on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                f.write('"""\n\n')
                f.write('models = ')

                json_str = json.dumps(output_data, indent=4)
                
                # Additional formatting for better readability
                json_str = json_str.replace('"data": [', '"data": [\n        ')
                json_str = json_str.replace('}, {', '},\n        {')
                json_str = json_str.replace('}]', '}\n    ]')
                
                f.write(json_str)
                f.write('\n')

            return free_models
            
        except Exception as file_error:
            print(f"Error writing to file: {file_error}")
            return None
            
    except requests.exceptions.RequestException as req_error:
        print(f"Error fetching models from OpenRouter: {req_error}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None