available = [
'llama-3.3-70b-turbo', 'phi-4', 'deepseek-r1', 'deepseek-v3',
'deepseek-r1-llama-3.3-70b-distill', 'lunaris-l3-8b', 'wazardlm-2-8x22b',
'mythomax-13b', 'mistral-nemo', 'gemini-1.5-flash', 'gemini-1.5-pro',
'gemma-2-27b', 'gemma-2-9b-turbo', 'llama-3-70b-intruct', 'llama-3.1-70b',
'llama-3.1-70b-instruct', 'llama-3.1-8b-turbo', 'llama-3.3-70b', 'qwen-2.5-coder-32b',
'qwq-32b'
]


async def poli(prompt, random, requests):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    response = requests.get(image_url)
    return response.url

async def generate_api_key(random, string):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    api_key = f'XET-{random_string}'
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

async def get_id(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    id_doc = collection.find_one({"apitoken": token})
    user_id = "None" if not id_doc["userid"] else id_doc["userid"]
    return user_id


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

async def log_image(user_id, engine, img_url, prompt, headers, httpx, datetime):
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
            print("Error in api_utils.py at line 145.")
            print(f"WARNING: FAILED TO LOG IMAGE, ERROR: {exc.response.text}")
        except Exception as e:
            print("Error in api_utils.py at line 147.")
            print(f"WARNING: An unexpected error occurred: {str(e)}")

async def log_message(title, description, color, headers, httpx, datetime):
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

async def register_user(email, password, verification_code, exp,  mongodb, datetime):
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


async def send_verify_email(to_email, email_from, password, code, MIMEMultipart, MIMEText, smtplib):
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

async def get_account_info(jwt_token, mongodb, datetime):
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

    if model == 'llama-3.3-70b-turbo': return "1334027674041188403"
    if model == "phi-4" : return "1269268810452697171"
    if model == 'deepseek-v3' : return "1267667453400322048"
    if model == 'deepseek-r1' : return "1334014377531150417"
    if model == 'deepseek-r1-llama-3.3-70b-distill' : return "1335829304872796171"
    if model == 'lunaris-l3-8b' : return "1335840965776244777"
    if model == 'wazardlm-2-8x22b' : return "1335847430163402832"
    if model == 'mythomax-13b' : return "1335849207571021914"
    if model == 'mistral-nemo' : return "1335848676609757244"
    if model == "gemini-1.5-flash" : return "1335983706569179176"
    if model == 'gemini-1.5-pro' : return "1335984488437518398"
    if model == 'gemma-2-27b' : return "1335981921481658440"
    if model == 'gemma-2-9b-turbo' : return "1335982976005312613"
    if model == 'llama-3-70b-intruct' : return "1336333593244602480"
    if model == 'llama-3.1-70b' : return "1336332553023524875"
    if model == 'llama-3.1-70b-instruct' : return "1336333074031448217"
    if model == 'llama-3.1-8b-turbo' : return "1335985846104625183"
    if model == 'llama-3.3-70b' : return "1336327195857256510"
    if model == 'qwen-2.5-coder-32b' : return "1336328341569015888"
    if model == 'qwq-32b' : return "1336327778693288087"

    else: return "error"