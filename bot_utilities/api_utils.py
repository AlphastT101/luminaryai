from openai import OpenAI
# from bot_utilities.api_prompt import prompt
import random
import string
import requests



open_models = {
    "openchat-7b":"openchat/openchat-7b:free",
    "openchat-3.5-7b":"openchat/openchat-7b:free",
    "qwen-2-7b-instruct":"qwen/qwen-2-7b-instruct:free",
    "gemma-2-9b-it":"google/gemma-2-9b-it:free",
    "phi-3-mini-128k-instruct":"microsoft/phi-3-mini-128k-instruct:free",
    "phi-3-medium-128k-instruct":"microsoft/phi-3-medium-128k-instruct:free",
    "llama-3-8b-instruct":"meta-llama/llama-3-8b-instruct:free",
    "gemma-7b-it":"google/gemma-7b-it:free",
    "nous-capybara-7b":"nousresearch/nous-capybara-7b:free",
    "mythomist-7b":"gryphe/mythomist-7b:free",
    "toppy-m-7b":"undi95/toppy-m-7b:free",
    "zephyr-7b-beta":"huggingfaceh4/zephyr-7b-beta:free",
    "mistral-7b-instruct":"mistralai/mistral-7b-instruct:free"
}

open_available = [
'openchat-7b', 'openchat-3.5-7b', 'qwen-2-7b-instruct', 'gemma-2-9b-it', 'phi-3-mini-128k-instruct',
'phi-3-medium-128k-instruct', 'llama-3-8b-instruct', 'gemma-7b-it', 'nous-capybara-7b', 'mythomist-7b',
'toppy-m-7b', 'zephyr-7b-beta', 'mistral-7b-instruct',
]

def poli(prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    response = requests.get(image_url)
    return response.url

async def generate_api_key(prefix='luminary'):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=40))
    api_key = f'{prefix}-{random_string}'
    return api_key


def check_token(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]

    result = collection.find_one({"apitoken": token})
    if result: return True
    else: return False

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

def get_id(mongodb, token):
    db = mongodb["lumi-api"]
    collection = db["apitokens"]
    id_doc = collection.find_one({"apitoken": token})
    user_id = "None" if not id_doc["userid"] else id_doc["userid"]
    return user_id


def gen_text(api_key, msg_history, model):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    completion = client.chat.completions.create(
        model=open_models[model],
        messages=msg_history
    )

    return completion.choices[0].message.content